## happy path
* greet
  - utter_greet
* mood_great
  - utter_happy

## sad path 1
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* affirm
  - utter_happy

## sad path 2
* greet
  - utter_greet
* mood_unhappy
  - utter_cheer_up
  - utter_did_that_help
* deny
  - utter_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot

## open incident
* greet
    - utter_greet
* open_incident
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}

## New Story

* open_incident
    - open_incident_form
    - action_deactivate_form
    - form{"name":null}
    - slot{"requested_slot":null}
