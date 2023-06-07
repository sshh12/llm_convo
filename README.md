# llm_convo

Use ChatGPT over Twilio to create an AI phone agent (works for incoming or outgoing calls).

### How it works

Twilio Webhook -> Flask app -> Twilio Media Stream (websocket) -> Whisper -> ChatGPT API -> Google TTS -> Twilio Play Audio

### Setup

1. `pip install git+https://github.com/sshh12/llm_convo`
2. Environment Variables

```
OPENAI_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

### Demo

Setup a Haiku hotline with Twilio that can be called like any other phone number.

```python
from gevent import monkey

monkey.patch_all()
from llm_convo.agents import OpenAIChat, TwilioCaller
from llm_convo.twilio_io import TwilioServer
from llm_convo.conversation import run_conversation
import logging
import time

logging.getLogger().setLevel(logging.INFO)

tws = TwilioServer(remote_host="abcdef.ngrok.app", port=8080, static_dir=r"/path/to/static")
# Point twilio voice webhook to https://abcdef.ngrok.app/audio/incoming-voice
tws.start()
agent_a = OpenAIChat(
    system_prompt="You are a Haiku Assistant. Answer whatever the user wants but always in a rhyming Haiku.",
    init_phrase="This is Haiku Bot, how can I help you.",
)
# agent_a = OpenAIChat(
#     system_prompt="""
# You are an ordering bot that is going to call a pizza place an order a pizza.
# When you need to say numbers space them out (e.g. 1 2 3) and do not respond with abbreviations.
# If they ask for information not known, make something up that's reasonable.

# The customer's details are:
# * Address: 1234 Candyland Road, Apt 506
# * Credit Card: 1234 5555 8888 9999 (CVV: 010)
# * Name: Bob Joe
# * Order: 1 large pizza with only pepperoni
# """,
#     init_phrase="Hi, I would like to order a pizza.",
# )


def run_chat(sess):
    agent_b = TwilioCaller(sess)
    while not agent_b.session.media_stream_connected():
        time.sleep(0.1)
    run_conversation(agent_a, agent_b)


tws.on_session = run_chat

# You can also have ChatGPT actually start the call, e.g. for automated ordering
# tws.start_call("+18321231234")
```

# solv notes

- need to `brew install portaudio`
- install ngrok (brew)
- run ngrok and configure twilio with ngrok url
- pip install gevent python-dotenv twilio flask flask-sock
- lots of typos (need llm\_ in front of some things)

# instructions for setting up twilio webhook + ngrok

To point your Twilio Voice webhook to an ngrok URL, follow these steps:

1. Install and set up ngrok on your local machine. Ngrok provides a secure tunnel to expose your local development server to the internet. You can download ngrok from the official website: https://ngrok.com/download.

2. Start ngrok by running the following command in your terminal:

```
ngrok http 8000
```

Replace 8000 with the port number where your local development server is running. Ensure that your local server is running before starting ngrok.

3. Once ngrok is running, it will display a Forwarding URL. It should look something like this:

```
Forwarding                    https://abcdef.ngrok.io -> http://localhost:8000
```

Note the HTTPS URL provided by ngrok (https://abcdef.ngrok.io in this example).

4. Go to the Twilio Console (https://www.twilio.com/console) and navigate to the phone number you want to configure.

5. In the Phone Number settings, locate the Voice section and find the "A CALL COMES IN" field. Enter the ngrok URL followed by the path to your voice webhook endpoint. For example:

```

https://abcdef.ngrok.io/audio/incoming-voice
```

Replace https://abcdef.ngrok.io with your ngrok URL and /audio/incoming-voice with the path to your voice webhook endpoint.

6. Save the changes to apply the new webhook URL.

Now, when a voice call comes to your Twilio phone number, Twilio will forward the call to the ngrok URL, which will then redirect it to your local development server running on the specified port.

Remember that ngrok generates a temporary URL for each session, and it may change every time you restart ngrok. Make sure to update the webhook URL in the Twilio Console accordingly whenever you restart ngrok.
