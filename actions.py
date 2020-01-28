from typing import Dict, Text, Any, List, Union
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

import requests
import json
import os

snow_user = os.getenv("SNOW_USER")
snow_pw = os.getenv("SNOW_PW")
snow_instance = os.getenv("SNOW_INSTANCE")

base_api_url = "https://{}/api/now".format(snow_instance)


def email_to_sysid(email):
    lookup_url = f"{base_api_url}/table/sys_user?sysparm_limit=1&email={email}"
    user = snow_user
    pwd = snow_pw
    # Set proper headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }  # noqa: 501
    # Do the HTTP request
    response = requests.get(lookup_url, auth=(user, pwd), headers=headers)
    results = response.json()["result"]
    return results


def create_incident(description, short_description, priority, caller):
    incident_url = "https://{}/api/now/table/incident".format(snow_instance)
    user = snow_user
    pwd = snow_pw
    # Set proper headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }  # noqa: 501
    data = {
        "opened_by": caller,
        "short_description": short_description,
        "description": description,
        "urgency": priority,
        "caller_id": caller,
        "comments": description,
    }
    response = requests.post(
        incident_url, auth=(user, pwd), headers=headers, data=json.dumps(data)
    )
    return response


class OpenIncidentForm(FormAction):
    def name(self) -> Text:
        return "open_incident_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["email", "problem_description", "incident_title", "priority"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "email": self.from_entity(entity="email"),
            "problem_description": self.from_text(intent="inform"),
            "incident_title": self.from_text(intent="inform"),
            "priority": self.from_entity(entity="priority"),
        }

    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate email is in ticket system."""

        caller = email_to_sysid(value)

        if len(caller) == 1:
            # validation succeeded, set the value of the "email" slot to value
            return {"email": value}
        else:
            dispatcher.utter_template("utter_no_email", tracker)
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"email": None}

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        priority = tracker.get_slot("priority")
        email = tracker.get_slot("email")
        problem_description = tracker.get_slot("problem_description")
        incident_title = tracker.get_slot("incident_title")

        incident_number = ""
        snow_priority = None

        print(f"The email is: {email}")

        # Check priority and set number value accordingly
        if priority == "low":
            snow_priority = "3"
        elif priority == "medium":
            snow_priority = "2"
        else:
            snow_priority = "1"

        print(f"The snow priority is: {snow_priority}")

        caller = email_to_sysid(email)
        response = create_incident(
            description=problem_description,
            short_description=incident_title,
            priority=snow_priority,
            caller=caller[0]["sys_id"],
        )
        incident_number = response.json()["result"]["number"]
        message = (
            f"Successfully opened up incident {incident_number} for you.  "
            f"Someone will reach out soon."
        )
        # utter submit template
        dispatcher.utter_message(message)
        return []
