# gpt-convo

Use ChatGPT over Twilio to create an AI phone agent (works for incoming or outgoing calls).

### How it works

Twilio Webhook -> Flask app -> Twilio Media Stream (websocket) -> Whisper -> ChatGPT API -> Google TTS -> Twilio Play Audio

### Setup

1. `pip install -r requirements.txt`
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

from convo.agents import OpenAIChat, TwilioCaller
from convo.twilio_io import TwilioServer
from convo.conversation import run_conversation
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
