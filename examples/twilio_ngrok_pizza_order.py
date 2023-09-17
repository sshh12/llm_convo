from gevent import monkey

monkey.patch_all()

import logging
import argparse
import tempfile
import os
import time
import sys
from llm_convo.agents import OpenAIChat, TwilioCaller
from llm_convo.audio_input import get_whisper_model
from llm_convo.twilio_io import TwilioServer
from llm_convo.conversation import run_conversation
from pyngrok import ngrok


def main(port, remote_host, start_ngrok, phone_number):
    if start_ngrok:
        ngrok_http = ngrok.connect(port)
        remote_host = ngrok_http.public_url.split("//")[1]

    static_dir = os.path.join(tempfile.gettempdir(), "twilio_static")
    os.makedirs(static_dir, exist_ok=True)

    logging.info(
        f"Starting server at {remote_host} from local:{port}, serving static content from {static_dir}, will call {phone_number}"
    )
    logging.info(f"Set call webhook to https://{remote_host}/incoming-voice")

    input(" >>> Press enter to start the call after ensuring the webhook is set. <<< ")

    tws = TwilioServer(remote_host=remote_host, port=port, static_dir=static_dir)
    tws.start()
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
        agent_b = TwilioCaller(sess, thinking_phrase="One moment.")
        while not agent_b.session.media_stream_connected():
            time.sleep(0.1)
        run_conversation(agent_a, agent_b)
        sys.exit(0)

    tws.on_session = run_chat
    tws.start_call(phone_number)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--phone_number", type=str)
    parser.add_argument("--preload_whisper", action="store_true")
    parser.add_argument("--start_ngrok", action="store_true")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--remote_host", type=str, default="localhost")
    args = parser.parse_args()
    if args.preload_whisper:
        get_whisper_model()
    main(args.port, args.remote_host, args.start_ngrok, args.phone_number)
