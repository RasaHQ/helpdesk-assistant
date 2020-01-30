# helpdesk_assistant
Basic demo use case showing Rasa with Service Now API calls to open incidents.

# Setup locally with Python
1. Setup a virtualenv of your choice ensuring to use python3 then run the following in the first terminal to setup the action server:

**You have to deactivate after installation due to tensorflow and other libraries requiring it to start working**

Also note how we are setting 3 exports, these are used in the script to connect to your service now instance.

`snow_instance` - This is just the instance address, you don't need the leading https.

`snow_user` - The username of the service account this action code will use to open a incident.

`snow_pw` - The password of the service account this action code will use to open a incident.

```
export SNOW_INSTANCE=devxxx.service-now.com
export SNOW_USER=user
export SNOW_PW=password
rasa run actions --actions action (Ensure you have your exports exported on the shell you run here)
```

2. On another terminal screen run the following to run duckling in a container:

```
docker run -p 8000:8000 rasa/duckling

```

3. Now finally we can train our model then start up the shell to test it in a 3rd terminal:

```
source venv/bin/activate
pip install -r requirements.txt
deactivate
source venv/bin/activate
rasa train --debug
rasa shell --debug
```

# Docker Deployment Information
TODO
