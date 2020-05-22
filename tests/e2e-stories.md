## bot challenge
* bot_challenge: Are you a bot?
  - utter_iamabot

## out of scope
* out_of_scope: I want a pizza
  - utter_out_of_scope

## open incident
* greet: hello
    - utter_greet
    - utter_help
* open_incident: I need to open an incident
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}

## open password reset incident
* password_reset: I'm having issues with my password
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}


## email incident
* greet: hello
    - utter_greet
    - utter_help
* problem_email: I have a problem with my email
    - open_incident_form
    - form{"name": "open_incident_form"}
    - form{"name": null}

## interrupted
* problem_email: I have a problem with my email
    - open_incident_form
    - form{"name": "open_incident_form"}
* help: help
    - utter_help
    - open_incident_form
    - form{"name": null}

## site FAQs
* site_hours: what are the site hours
  - utter_site_hours
* site_cafeteria_menu: what is the menu
  - utter_site_cafeteria_menu
* site_map: is there a site map
  - utter_site_map
* site_emergency: where is the site emergency contact
  - utter_site_emergency
* site_security: how do I reach site security
  - utter_site_security

## admin stories
* f1_score: show confidence scores
  - action_f1_score
* show_slots: show me the current slot values
  - action_show_slots