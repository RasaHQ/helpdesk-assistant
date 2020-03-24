# Rasa Helpdesk Assistant Demo

This is a basic demo bot showing Rasa with Service Now API calls to open incidents.

Here is an example of a conversation you can have with this bot:

![Screenshot](./screenshots/demo_ss.png?raw=true)

## Setup

### Install the dependencies

In a Python3 virtual environment run:

```bash
pip install -r requirements.txt
```

### Connect to a ServiceNow instance

You can get your own free Service Now Developer instance to test this with [here](https://developer.servicenow.com/app.do#!/home)

To connect to your service now instance, configure the following in `snow_credentials.yml`:

- `snow_instance` - This is just the instance address, you don't need the leading https.

- `snow_user` - The username of the service account this action code will use to open a incident.

- `snow_pw` - The password of the service account this action code will use to open a incident.

- `localmode` -  Whether the action server should **not** try to reach out to a `snow_instance` based on the credentials in `snow_credentials.yml`. When set to `True` (default in the code), it will just take all the data in and message out the information that would normally be sent.

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

```sh
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

## Docker Deployment of Action Server

A Dockerfile is provided, so you can build a docker image for the action server, to use in production deployments.

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
