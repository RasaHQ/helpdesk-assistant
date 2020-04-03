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

## story_version
* version
  - utter_version
  - action_version

## f1_score
* f1_score
  - action_f1_score

## show_slots
* show_slots
  - action_show_slots

## restart
* restart
  - utter_restart
  - action_restart

## reset_slots
* reset_slots
  - action_reset_slots

## site hours
* site_hours
  - utter_site_hours

## site cafeteria 
* site_cafeteria_menu
  - utter_site_cafeteria_menu

## site map
* site_map
  - utter_site_map

## site emergency
* site_emergency
  - utter_site_emergency

## site security
* site_security
  - utter_site_security
