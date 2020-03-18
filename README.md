# Rasa Helpdesk Assistant Demo
![Lint and Test](https://github.com/RasaHQ/helpdesk-assistant/workflows/Lint%20and%20Test/badge.svg)

This is a basic demo bot showing Rasa with Service Now API calls to open incidents.  You can get your own free Service Now Developer instance to test this with [here](https://developer.servicenow.com/app.do#!/home)

# Screenshot Example
![Screenshot](./screenshots/demo_ss.png?raw=true)


## To install the dependencies:

In a virtual environment (`python >=3.5`) run:
```bash
pip install -r requirements.txt
```

## Connect to a ServiceNow instance

To connect to your service now instance, configure the following in `snow_credentials.yml`:

- `snow_instance` - This is just the instance address, you don't need the leading https.

- `snow_user` - The username of the service account this action code will use to open a incident.

- `snow_pw` - The password of the service account this action code will use to open a incident.

- `localmode` -  Whether the action server should **not** try to reach out to a `snow_instance` based on the credentials in `snow_credentials.yml`. When set to `True` (default in the code), it will just take all the data in and message out the information that would normally be sent. 


## To run the bot:

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
```
rasa shell --debug
```


Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working 
under the hood. You can also add this flag to the action server command. To simply talk to the bot, you can remove this flag.


# Docker Deployment of Action Server
You can also build and run a docker image for the action server instead of running it in a seperate terminal:

```bash
docker build . -t <name of your custom image>:<tag of your custom image>
```

You can then run the action server with:

```bash
docker run <name of your custom image>:<tag of your custom image>
```


## Things you can ask the bot

The bot currently has one skill which can be triggered in two ways.

It also has a limited ability to switch skills mid-transaction and then return to the transaction at hand.

For the purposes of illustration, the bot recognises the following fictional credit card accounts:

- `gringots`
- `justice bank`
- `credit all`
- `iron bank`

It recognises the following payment amounts (besides actual currency amounts):

- `minimum balance`
- `current balance`

It recognises the following vendors (for spending history):

- `Starbucks`
- `Amazon`
- `Target`

You can change any of these by modifying `actions.py` and the corresponding NLU data.


# Dialog Example
With `localmode=True`: 

```


```
With `localmode=False`:

With a Service Now instance connected, it will check if the email address is in the instance database and provide an incident number for the final response:

```

```
