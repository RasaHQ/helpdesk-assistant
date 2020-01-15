# helpdesk_assistant
Basic demo use case showing Rasa X with Service Now API calls to open incidents.

# Setup
Setup a virtualenv of your choice ensuring to use python3 then run the following:

```
source venv/bin/activate
pip install rasa-x --extra-index-url https://pypi.rasa.com/simple
deactivate
source venv/bin/activate

export SNOW_INSTANCE=devxxx.service-now.com
export SNOW_USER=user
export SNOW_PW=password

docker run -p 8000:8000 rasa/duckling

rasa run actions --actions action (Ensure you have your exports exported on the shell you run here)

rasa x
```

After Rasa X is running you can train and then test the chatbot from the UI.

**You have to deactivate after installation due to tensorflow and other libraries requiring it to start working**

Also note how we are setting 3 exports, these are used in the script to connect to your service now instance.

`snow_instance` - This is just the instance address, you don't need the leading https.

`snow_user` - The username of the service account this action code will use to open a incident.

`snow_pw` - The password of the service account this action code will use to open a incident.

This will install Rasa X and all the required dependencies.

# Docker Deployment Information
If running this on the Rasa docker setup, I already have the `Dockerfile` in this repository created as a image which can be used `realbtotharye/helpdesk_action` you just need to supply the same env vars: 

`SNOW_INSTANCE`

`SNOW_USER`

`SNOW_PW`

You can set these via the existing `docker-compose.yml` file that is present from installing via instructions [Rasa X Docker Deploy](https://rasa.com/docs/rasa-x/deploy/#quick-installation) by modifying it.

You want to modify the section to be updated with the `env_file` and use the existing `.env` as well and just put your `SNOW_INSTANCE` and such vars inside this file.

See how we update the app service to now have the `env_file` section?  This will bring in our vars from that file and we can use 1 env file to manage all the vars for the services.


```
app:
    restart: always
    image: "rasa/rasa-x-demo:${RASA_X_DEMO_VERSION}"
    expose:
      - "5055"
    depends_on:
      - rasa-production
    env_file:
     - .env
```

**Remember per the Rasa docs you need to create a docker-compose.override.yml file and supply the updated image there**

Example of override:
```
version: '3.4'
services:
  app:
    image: realbtotharye/helpdesk_action
```

# Example Conversation Flow
![Rasa Screenshot](https://github.com/btotharye/helpdesk_assistant/blob/master/screenshots/demo_ss.png)
