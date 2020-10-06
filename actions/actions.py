import logging
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher, Action
from rasa_sdk.forms import FormAction, REQUESTED_SLOT, FormValidationAction
from rasa_sdk.events import AllSlotsReset, SlotSet, EventType
from actions.snow import SnowAPI
import random


logger = logging.getLogger(__name__)
vers = "vers: 0.1.0, date: Apr 2, 2020"
logger.debug(vers)

snow = SnowAPI()
localmode = snow.localmode
logger.debug(f"Local mode: {snow.localmode}")


def custom_request_next_slot(
    form,
    dispatcher: "CollectingDispatcher",
    tracker: "Tracker",
    domain: Dict[Text, Any],
) -> Optional[List[EventType]]:
    """Request the next slot and utter template if needed,
        else return None"""

    for slot in form.required_slots(tracker):
        if form._should_request_slot(tracker, slot):
            logger.debug(f"Request next slot '{slot}'")
            if slot == "email" and tracker.get_slot("previous_email"):
                dispatcher.utter_message(
                    template=f"utter_ask_use_previous_email_{slot}",
                    **tracker.slots,
                )
            else:
                dispatcher.utter_message(
                    template=f"utter_ask_{slot}", **tracker.slots
                )
            return [SlotSet(REQUESTED_SLOT, slot)]

    return None


def _validate_email(
    value: Text,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any],
) -> Dict[Text, Any]:
    """Validate email is in ticket system."""
    if not value:
        return {"email": None, "previous_email": None}
    elif isinstance(value, bool):
        value = tracker.get_slot("previous_email")

    if localmode:
        return {"email": value}

    results = snow.email_to_sysid(value)
    caller_id = results.get("caller_id")

    if caller_id:
        return {"email": value, "caller_id": caller_id}
    elif isinstance(caller_id, list):
        dispatcher.utter_message(template="utter_no_email")
        return {"email": None}
    else:
        dispatcher.utter_message(results.get("error"))
        return {"email": None}


class ValidateOpenIncidentForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_open_incident_form"

    # def request_next_slot(
    #     self,
    #     dispatcher: "CollectingDispatcher",
    #     tracker: "Tracker",
    #     domain: Dict[Text, Any],
    # ) -> Optional[List[EventType]]:
    #
    #     return custom_request_next_slot(self, dispatcher, tracker, domain)

    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate email is in ticket system."""
        return _validate_email(value, dispatcher, tracker, domain)

    def validate_priority(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate priority is a valid value."""

        if value.lower() in snow.priority_db():
            return {"priority": value}
        else:
            dispatcher.utter_message(template="utter_no_priority")
            return {"priority": None}


class ActionOpenIncident(Action):
    def name(self) -> Text:
        return "action_open_incident"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Create an incident and return details or
        if localmode return incident details as if incident
        was created
        """

        priority = tracker.get_slot("priority")
        email = tracker.get_slot("email")
        problem_description = tracker.get_slot("problem_description")
        incident_title = tracker.get_slot("incident_title")
        confirm = tracker.get_slot("confirm")
        if not confirm:
            dispatcher.utter_message(
                template="utter_incident_creation_canceled"
            )
            return [AllSlotsReset(), SlotSet("previous_email", email)]

        if localmode:
            message = (
                f"An incident with the following details would be opened "
                f"if ServiceNow was connected:\n"
                f"email: {email}\n"
                f"problem description: {problem_description}\n"
                f"title: {incident_title}\npriority: {priority}"
            )
        else:
            snow_priority = snow.priority_db().get(priority)
            response = snow.create_incident(
                description=problem_description,
                short_description=incident_title,
                priority=snow_priority,
                email=email,
            )
            incident_number = (
                response.get("content", {}).get("result", {}).get("number")
            )
            if incident_number:
                message = (
                    f"Successfully opened up incident {incident_number} "
                    f"for you. Someone will reach out soon."
                )
            else:
                message = (
                    f"Something went wrong while opening an incident for you. "
                    f"{response.get('error')}"
                )
        dispatcher.utter_message(message)
        return [AllSlotsReset(), SlotSet("previous_email", email)]


class IncidentStatusForm(FormAction):
    def name(self) -> Text:
        return "incident_status_form"

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        return custom_request_next_slot(self, dispatcher, tracker, domain)

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["email"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "email": [
                self.from_entity(entity="email"),
                self.from_intent(value=True, intent="affirm"),
                self.from_intent(value=False, intent="deny"),
            ]
        }

    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate email is in ticket system."""
        return _validate_email(value, dispatcher, tracker, domain)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Look up all incidents associated with email address
           and return status of each"""

        email = tracker.get_slot("email")

        incident_states = {
            "New": "is currently awaiting triage",
            "In Progress": "is currently in progress",
            "On Hold": "has been put on hold",
            "Closed": "has been closed",
        }
        if localmode:
            status = random.choice(list(incident_states.values()))
            message = (
                f"Since ServiceNow isn't connected, I'm making this up!\n"
                f"The most recent incident for {email} {status}"
            )
        else:
            incidents_result = snow.retrieve_incidents(email)
            incidents = incidents_result.get("incidents")
            if incidents:
                message = "\n".join(
                    [
                        f'Incident {i.get("number")}: '
                        f'"{i.get("short_description")}", '
                        f'opened on {i.get("opened_at")} '
                        f'{incident_states.get(i.get("incident_state"))}'
                        for i in incidents
                    ]
                )

            else:
                message = f"{incidents_result.get('error')}"

        dispatcher.utter_message(message)
        return [AllSlotsReset(), SlotSet("previous_email", email)]
