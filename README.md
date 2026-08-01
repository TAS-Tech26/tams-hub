# tams-hub
Orchestrator layer for events using Kahoot-replica.

### How do you set this up?
1. Create a venv & activate (Setup venv using `python -m venv <venv_name>`, then go into the venv/Scripts & activate)
2. Install requirements.txt
3. Set up the env files. For this you'll need B2B_HOST_SECRET, HUB_SECRET_KEY & SECRET_KEY.

### How does this work?
This is supposed to be the orchestrator layer for all the events that will be using Kahoot-replica. For whichever phase does the event use Kahoot-replica, the data flow can be handled accordingly.

### Things to remember
This orchestrator layer is currently being used by Bid2Build (B2B) & Kahoot-replica.
- Set this up on the default port (8000), Kahoot-replica on 8001 & B2B on 8002.
- Put down these service URLs as well in the same env file (HUB_SERVICE_URL, KAHOOT_SERVICE_URL, B2B_SERVICE_URL).

Activate venv & run using `python manage.py runserver <port_no>`.
