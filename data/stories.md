## out of scope path
* out_of_scope
  - utter_out_of_scope

## help
* help
  - utter_help

## thank
* thank
  - utter_welcome

## happy path
* greet
  - utter_greet
  - utter_help

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot


## incident form
* open_incident OR password_reset OR problem_email
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}

## incident form interrupted
* open_incident OR password_reset OR problem_email
    - open_incident_form
    - form{"name":"open_incident_form"}
* help
    - utter_help
    - open_incident_form
    - form{"name":null}

## incident form interrupted
* open_incident OR password_reset OR problem_email
    - open_incident_form
    - form{"name":"open_incident_form"}
* out_of_scope
    - utter_out_of_scope
    - open_incident_form
    - form{"name":null}

## story_version
* version
  - utter_version
  - action_version

## story restart
* restart
  - action_restart
  - utter_restart
  - action_session_start
  - utter_greet

## site faq
* site_faq
  - respond_site_faq