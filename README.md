# Rasa Helpdesk Assistant Example

This is a Rasa chatbot example demonstrating how to build an AI assistant for an IT Helpdesk. It includes an integration with the Service Now API to open incident reports. Below is an example conversation, showing the bot helping a user open a support ticket. You can use this chatbot as a starting point for building customer service assistants or as a template for collecting required pieces of information from a user before making an API call. 

Here is an example of a conversation you can have with this bot:

![Screenshot](./screenshots/demo_ss.png?raw=true)

## Setup

### Install the dependencies

In a Python3 virtual environment run:

```bash
pip install -r requirements.txt
```

### Optional: Connect to a ServiceNow instance

You can run this bot without connecting to a ServiceNow instance, in which case it will
send responses without creating an incident. To run the bot  without connecting ServiceNow,
you don't need to change anything in `actions/snow_credentials.yml`; `localmode` should already be set
to `true`

If you do want to connect to ServiceNow, you can get your own free Developer instance 
to test this with [here](https://developer.servicenow.com/app.do#!/home)

To connect to your ServiceNow instance, configure the following in `actions/snow_credentials.yml`:

- `snow_instance` - This is just the instance address, you don't need the leading https.

- `snow_user` - The username of the service account this action code will use to open a incident.

- `snow_pw` - The password of the service account this action code will use to open a incident.

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

The bot has one main skill, i.e. opening an incident in ServiceNow.
For the purposes of illustration, the bot recognizes the following as requests to open an incident:

1. Asking to open an incident directly e.g. "I want to open an incident"
2. Asking about a problem resetting their password e.g. "I can't reset my password"
3. Asking about a problem with outlook/email e.g. "I can't log in to my outlook"

Take a look at `data/nlu.md` to see what the bot is currently trained to recognize.

It can also respond to requests for help (e.g. "help me")

## Example conversations

With `localmode=True`:

```sh
Bot loaded. Type a message and press enter (use '/stop' to exit):
Your input ->  hi
    Hello
    I can help you open a service request ticket. You can ask me things like "Open an incident",
    "Help me reset my password", or "I'm having a issue with my email."
Your input ->  i have a problem with my email
    What is your email address to lookup for creating the incident?
Your input ->  anything@example.com
    ? What is the priority of this issue?  3: high (/inform{"priority":"high"})      # This is a button
    What is the problem description for the issue?
Your input ->  can't log in to outlook
    An incident with the following details would be opened if ServiceNow was connected:
    email: anything@example.com
    problem description: can't log in to outlook
    title: Problem with email
    priority: high
Your input ->  bye!
    Bye
```

With `localmode=False`:

With a Service Now instance connected, it will check if the email address is in the instance database and provide an incident number for the final response:

```
Your input ->  help me reset my password
    What is your email address to lookup for creating the incident?
Your input ->  idontexist@example.com
    Sorry, "idontexist@example.com" isn't in our incident management system. Please try again.
    What is your email address to lookup for creating the incident?
Your input ->  abraham.lincoln@example.com
    ? What is the priority of this issue?  Type out your own message...
Your input ->  low
    Successfully opened up incident INC0010016 for you.  Someone will reach out soon.
Your input ->  thanks!
    You're welcome!
```

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

It is recommended to use an automated CI/CD process to keep your action server up to date in a production environment.
