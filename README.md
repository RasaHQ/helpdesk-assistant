# Rasa Helpdesk Assistant Demo
![Lint and Test](https://github.com/RasaHQ/helpdesk-assistant/workflows/Lint%20and%20Test/badge.svg)

Basic demo use case showing Rasa with Service Now API calls to open incidents.  You can get your own free Service Now Developer instance to test this with [here](https://developer.servicenow.com/app.do#!/home)

# Screenshot Example
![Screenshot](https://github.com/RasaHQ/helpdesk-assistant/blob/master/screenshots/demo_ss.png?raw=true)


## Setup locally with Python
Setup a virtualenv of your choice ensuring to use python3 then install the requirements:

```
pip install -r requirements.txt
```

To connect to your service now instance, configure the following in `snow_credentials.yml`:

- `snow_instance` - This is just the instance address, you don't need the leading https.

- `snow_user` - The username of the service account this action code will use to open a incident.

- `snow_pw` - The password of the service account this action code will use to open a incident.

- `local_mode` - You can set this to `True` and the action server will not reach out to a Service Now instance, instead it will just take all the data in and message out the information that would normally be sent. By default this is set to `False` in the code and will try to reach out to a `snow_instance` based on the credentials in `snow_credentials.yml`.

## Train a model

```bash
rasa train
```

## Test the assistant

Terminal 1 - Action Server
```
rasa run actions --actions actions.actions
```

Terminal 2 - Duckling for Email Extraction
```
docker run -p 8000:8000 rasa/duckling
```

Terminal 3 - Rasa Shell
```
rasa run shell
```

# Docker Deployment Information
To build a docker image for the action server:

```bash
docker build . -t <name of your custom image>:<tag of your custom image>
```

You can then run the action server with:

```bash
docker run <name of your custom image>:<tag of your custom image>
```


# Dialog Example
In `local_mode=True` mode this is the dialog example.

```
Bot loaded. Type a message and press enter (use '/stop' to exit):

Your input ->  hello
Hello
I can help you open a case for your password reset or any other issue. You can say things like, help me reset my password, or I'm having a issue to get started.

Your input ->  help me reset my password
What is your email address to lookup for creating the ticket?

Your input ->  test@test.com

Ok what should the priority be?  Low, medium, or high?
Your input ->  medium

We would open a case with the following: email: test@test.com
problem description: password reset issue
title: Password Reset
priority: medium

```

For a Service Now connected flow its basically the same except for the final response:

```
Successfully opened up incident INCXXX for you.
Someone will reach out shortly.
```
