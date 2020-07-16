# Rasa Helpdesk Assistant Example

This is a Rasa chatbot example demonstrating how to build an AI assistant for an IT Helpdesk. It includes an integration with the Service Now API to open incident reports and check on incident report statuses. Below is an example conversation, showing the bot helping a user open a support ticket and query its status. You can use this chatbot as a starting point for building customer service assistants or as a template for collecting required pieces of information from a user before making an API call. 

Here is an example of a conversation you can have with this bot:

![Screenshot](./screenshots/demo_ss.png?raw=true)


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents** 

- [Rasa Helpdesk Assistant Example](#rasa-helpdesk-assistant-example)
  - [Setup](#setup)
    - [Install the dependencies](#install-the-dependencies)
    - [Optional: Connect to a ServiceNow instance](#optional-connect-to-a-servicenow-instance)
  - [Running the bot](#running-the-bot)
  - [Things you can ask the bot](#things-you-can-ask-the-bot)
  - [Example conversations](#example-conversations)
  - [Handoff](#handoff)
    - [Try it out](#try-it-out)
    - [How it works](#how-it-works)
    - [Bot-side configuration](#bot-side-configuration)
  - [Testing the bot](#testing-the-bot)
  - [Rasa X Deployment](#rasa-x-deployment)
    - [Action Server Image](#action-server-image)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Setup

### Install the dependencies

In a Python3 virtual environment run:

```bash
pip install -r requirements.txt
```

To install development dependencies, run:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

> With pre-commit installed, the `black` and `doctoc` hooks will run on every `git commit`. 
> If any changes are made by the hooks, you will need to re-add changed files and re-commit your changes.

### Optional: Connect to a ServiceNow instance

You can run this bot without connecting to a ServiceNow instance, in which case it will
send responses without creating an incident or checking the actual status of one.
To run the bot  without connecting ServiceNow,
you don't need to change anything in `actions/snow_credentials.yml`; `localmode` should already be set
to `true`

If you do want to connect to ServiceNow, you can get your own free Developer instance 
to test this with [here](https://developer.servicenow.com/app.do#!/home)

To connect to your ServiceNow developer instance, configure the following in `actions/snow_credentials.yml`:

- `snow_instance` - This is the address of the ServiceNow developer instance, you don't need the leading https.

- `snow_user` - The username of the service account for the ServiceNow developer instance

- `snow_pw` - The password of the service account for the ServiceNow developer instance

- `localmode` -  Whether the action server should **not** try to reach out to a `snow_instance` based on the credentials in `actions/snow_credentials.yml`. When set to `True` (default in the code), it will just take all the data in and message out the information that would normally be sent.

## Running the bot

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window:

```bash
rasa run actions
```

In another window, run the duckling server (for entity extraction):

```bash
docker run -p 8000:8000 rasa/duckling
```

Then to talk to the bot, run:

```bash
rasa shell --debug
```

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. You can also add this flag to the action server command. To simply talk to the bot, you can remove this flag.

## Things you can ask the bot

The bot has two main skills:
1. Opening an incident in ServiceNow.
2. Checking the status of incidents in ServiceNow by email address of the caller. It will prompt the user to re-use previously provided (during the chat session) email addresses, if any exist.
For the purposes of illustration, the bot recognizes the following as requests to open an incident:

1. Asking to open an incident directly e.g. "I want to open an incident"
2. Asking about a problem resetting their password e.g. "I can't reset my password"
3. Asking about a problem with outlook/email e.g. "I can't log in to my outlook"

Take a look at `data/nlu.md` to see what the bot is currently trained to recognize.

It can also respond to requests for help (e.g. "help me").

If configured, the bot can also hand off to another bot in response to the user asking for handoff. More [details on handoff](#handoff) below.

## Example conversations

With `localmode=true`:

```
Bot loaded. Type a message and press enter (use '/stop' to exit):
Your input ->  hi                                                          
    Hello!
    I can help you open a service request ticket, or check the status of your open incidents. 
    You can ask me things like: 
    - Open an incident 
    - Help me reset my password 
    - I'm having a issue with my email 
    - What's the status of the ticket I opened?
Your input ->  i have a problem with my email                              
    What is your email address?
Your input ->  anything@example.com                                        
    ? What is the priority of this issue?  
Your input -> 1: low (/inform{"priority":"low"})  
    What is the problem description for the issue?
Your input ->  Can't log in to my email                                    
    ? Should I open an incident with the following details? 
    email: anything@example.com 
    problem description: Can't log in to my email 
    title: Problem with email                                              
Your input -> priority: low  1: Yes (/affirm)                                        
    An incident with the following details would be opened if ServiceNow was connected:
    email: anything@example.com
    problem description: Can't log in to my email
    title: Problem with email
    priority: low
Your input ->  thanks. Can i check the status of my other tickets?         
    Would you like to use the last email address you used, anything@example.com?
Your input ->  Yes please                                                  
    Since ServiceNow isn't connected, I'm making this up!
    The most recent incident for anything@example.com is currently awaiting triage
```

With `localmode=false`:

With a Service Now instance connected, it will check if the email address is in the instance database and provide an incident number for the final response:

```
Your input ->  help me reset my password                                   
    What is your email address?
Your input ->  idontexist@example.com                                      
    Sorry, "idontexist@example.com" isn't in our incident management system. Please try again.
    What is your email address?
Your input ->  abraham.lincoln@example.com                                 
    ? What is the priority of this issue?  
Your input -> 3: high (/inform{"priority":"high"})                                                                        
    What is the problem description for the issue?
Your input ->  Password stuck in a loop                                    
    ? Should I open an incident with the following details? 
    email: abraham.lincoln@example.com 
    problem description: Password stuck in a loop 
    title: Problem resetting password                                      
    priority: high  
Your input ->  1: Yes (/affirm)                                       
    Successfully opened up incident INC0010008 for you.  Someone will reach out soon.
Your input ->  Can I check the status of my tickets?                       
    Would you like to use the last email address you used, abraham.lincoln@example.com?
Your input ->  Yes please                                                  
    Incident INC0010002: "Email Log in problem", opened on 2020-05-21 09:57:06 is currently in progress
    Incident INC0010008: "Problem resetting password", opened on 2020-05-21 12:12:49 is currently awaiting triage
Your input ->  thanks                                                      
    You're welcome!
```


## Handoff

This bot includes a simple skill for handing off the conversation to another bot or a human. 
This demo relies on [this fork of chatroom](https://github.com/RasaHQ/chatroom) to work, however you
could implement similar behaviour in another channel and then use that instead. See the chatroom README for
more details on channel-side configuration.


Using the default set up, the handoff skill enables this kind of conversation with two bots:

![handoff gif](handoff.gif)

### Try it out

The simplest way to use the handoff feature is to do the following:

1. Clone [chatroom](https://github.com/RasaHQ/chatroom) and [Financial-Demo](https://github.com/RasaHQ/Financial-Demo) alongside this repo
2. In the chatroom repo, install the dependencies:
```bash
yarn install
```
3. In the chatroom repo, build and serve chatroom:
```bash
yarn build
yarn serve
```
4. In the Financial-Demo repo, install the dependencies and train a model (see the Financial-Demo README)
5. In the Helpdesk-Assistant repo (i.e. this repo), run the rasa server and action server at the default ports (shown here for clarity)
   In one terminal window:
    ```bash
    rasa run --enable-api --cors "*" --port 5005 --debug
    ```
    In another terminal window:
    ```bash
    rasa run actions --port 5055 --debug
    ```
6. In the Financial-Demo repo, run the rasa server and action server at **the non-default ports shown below**
   In one terminal window:
    ```bash
    rasa run --enable-api --cors "*" --port 5006 --debug
    ```
    In another terminal window:
    ```bash
    rasa run actions --port 5056 --debug
    ```
7. Open `chatroom_handoff.html` in a browser to see handoff in action


### How it works

Using chatroom, the general approach is as follows:

1. User asks original bot for a handoff. 
2. The original bot handles the request and eventually 
   sends a message with the following custom json payload:
    ```
        {
            "handoff_host": "<url of handoff host endpoint>",
            "title": "<title for bot/channel handed off to>"
            }
    ```
    This message is not displayed in the Chatroom window.
3. Chatroom switches the host to the specified `handoff_host`
4. The original bot no longer receives any messages. 
5. The handoff host receives the message `/handoff{"from_host":"<original bot url">}`
6. The handoff host should be configured to respond to this message with something like,
   "Hi, I'm <so and so>, how can I help you??"
7. The handoff host can send a message in the same format as specified above to hand back to the original bot.
   In this case the same pattern repeats, but with
   the roles reversed. It could also hand off to yet another bot/human.

### Bot-side configuration

The "try it out" section doesn't require any further configuration; this section is for those
who want to change or further understand the set up.

For this demo, the user can ask for a human, but they'll be offered a bot (or bots) instead, 
so that the conversation looks like this:


For handoff to work, you need at least one "handoff_host". You can specify any number of handoff hosts in the file `actions/hanodff_config.yml`.
```
handoff_hosts:
    financial_demo:
      title: "Financial Demo"
      url: "http://localhost:5006"
    ## you can add more handoff hosts to this list e.g.
    # moodbot:
    #   title: "MoodBot"
    #   url: "http://localhost:5007"
```

Handoff hosts can be other locally running rasa bots, or anything that serves responses in the format that chatroom 
accepts. If a handoff host is not a rasa bot, you will of course want to update the response text to tell the user 
who/what they are being handed off to.

The [Financial-Demo](https://github.com/RasaHQ/Financial-Demo) bot has been set up to handle handoff in exactly the same way as Helpdesk-Assistant, 
so the simplest way to see handoff in action is to clone Financial-Demo alongside this repo.

If you list other locally running bots as handoff hosts, make sure the ports on which the various rasa servers & action servers are running do not conflict with each other. 


## Testing the bot

You can test the bot on the test conversations by running  `rasa test`. 
This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/conversation_tests.md`. 

## Rasa X Deployment

To [deploy helpdesk-assistant](https://rasa.com/docs/rasa/user-guide/how-to-deploy/), it is highly recommended to make use of the 
[one line deploy script](https://rasa.com/docs/rasa-x/installation-and-setup/one-line-deploy-script/) for Rasa X. As part of the deployment, you'll need to set up [git integration](https://rasa.com/docs/rasa-x/installation-and-setup/integrated-version-control/#connect-your-rasa-x-server-to-a-git-repository) to pull in your data and 
configurations, and build or pull an action server image.

### Action Server Image

You will need to have docker installed in order to build the action server image. If you haven't made any changes to the action code, you can also use
the [public image on Dockerhub](https://hub.docker.com/r/rasa/helpdesk-assistant) instead of building it yourself. 


See the Dockerfile for what is included in the action server image,

To build the image:

```bash
docker build . -t <name of your custom image>:<tag of your custom image>
```

To test the container locally, you can then run the action server container with:

```bash
docker run -p 5055:5055 <name of your custom image>:<tag of your custom image>
```

Once you have confirmed that the container works as it should, you can push the container image to a registry with `docker push`

It is recommended to use an[automated CI/CD process](https://rasa.com/docs/rasa/user-guide/setting-up-ci-cd) to keep your action server up to date in a production environment.
