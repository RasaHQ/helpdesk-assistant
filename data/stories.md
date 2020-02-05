## happy path
* greet
  - utter_greet

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

## greet and open incident
* greet
    - utter_greet
* open_incident
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}

## open incident
* open_incident
    - open_incident_form
    - action_deactivate_form
    - form{"name":null}
    - slot{"requested_slot":null}
