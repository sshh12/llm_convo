from gevent import monkey
from dotenv import load_dotenv
import os

load_dotenv()

monkey.patch_all()


# HERE
from llm_convo.agents import OpenAIChat, TwilioCaller
from llm_convo.twilio_io import TwilioServer
from llm_convo.conversation import run_conversation
import logging
import time


print("WERE DOING SOMETHING")

logging.getLogger().setLevel(logging.INFO)

tws = TwilioServer(
    remote_host="a8db-2603-8000-d100-14c9-810f-3c78-5c9a-603.ngrok.io",
    port=8080,
    static_dir=r"/static",
)
# Point twilio voice webhook to https://abcdef.ngrok.app/audio/incoming-voice
tws.start()

# agent_a = OpenAIChat(
#     system_prompt="You are a Haiku Assistant. Answer whatever the user wants but always in a rhyming Haiku.",
#     init_phrase="This is Haiku Bot, how can I help you.",
# )
agent_a = OpenAIChat(
    system_prompt="""
You are an ordering bot that is going to call a pizza place an order a pizza.
When you need to say numbers space them out (e.g. 1 2 3) and do not respond with abbreviations.
If they ask for information not known, make something up that's reasonable.

The customer's details are:
* Address: 1234 Candyland Road, Apt 506
* Credit Card: 1234 5555 8888 9999 (CVV: 010)
* Name: Bob Joe
* Order: 1 large pizza with only pepperoni
""",
    init_phrase="Hi, I would like to order a pizza.",
)


def run_chat(sess):
    print("running chat", sess)
    agent_b = TwilioCaller(sess)
    while not agent_b.session.media_stream_connected():
        time.sleep(0.1)
    run_conversation(agent_a, agent_b)


tws.on_session = run_chat

# You can also have ChatGPT actually start the call, e.g. for automated ordering
tws.start_call("+15035761174")
