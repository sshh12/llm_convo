import threading
import os
import base64
import json

from gevent.pywsgi import WSGIServer
from twilio.rest import Client
import simple_websocket
from flask import Flask
from flask_sock import Sock
import audioop

from convo.audio_input import WhisperTwilioStream


XML_MEDIA_STREAM = """
<Response>
    <Start>
        <Stream name="Audio Stream" url="wss://{host}/audiostream" />
    </Start>
    <Pause length="60"/>
</Response>
"""


class TwilioServer:
    def __init__(self, remote_host: str, port: int):
        self.app = Flask(__name__)
        self.sock = Sock(self.app)
        self.remote_host = remote_host
        self.port = port
        self.server_thread = threading.Thread(target=self._start)
        self.on_session = None

        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        self.phone = os.environ["TWILIO_PHONE_NUMBER"]
        self.client = Client(account_sid, auth_token)

        @self.app.route("/incoming-voice", methods=["POST"])
        def incoming_voice():
            return XML_MEDIA_STREAM.format(host=self.remote_host)

        @self.sock.route("/audiostream", websocket=True)
        def on_media_stream(ws):
            session = TwilioCallSession(ws, self.client)
            if self.on_session is not None:
                thread = threading.Thread(target=self.on_session, args=(session,))
                thread.start()
            session.start_session()

    def start_call(self, to_phone: str):
        self.client.calls.create(
            twiml=XML_MEDIA_STREAM.format(host=self.remote_host),
            to=to_phone,
            from_=to_phone,
        )

    def _start(self):
        print("Starting Twilio Server")
        WSGIServer(("0.0.0.0", self.port), self.app).serve_forever()

    def start(self):
        self.server_thread.start()


class TwilioCallSession:
    def __init__(self, ws, client: Client):
        self.ws = ws
        self.client = client
        self.sst_stream = WhisperTwilioStream()
        self.call = None

    def _read_ws(self):
        while True:
            try:
                message = self.ws.receive()
            except simple_websocket.ws.ConnectionClosed:
                print("ConnectionClosed")
                break
            if message is None:
                print("ConnectionClosed - None")
                break

            data = json.loads(message)
            if data["event"] == "connected":
                print("connect", data)
            elif data["event"] == "start":
                print("start", data)
                self.call = self.client.calls(data["start"]["callSid"])
            elif data["event"] == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if self.sst_stream.stream is not None:
                    self.sst_stream.stream.put(audioop.ulaw2lin(chunk, 2))
            elif data["event"] == "stop":
                print("Stopping...")
                break

    def say(self, text: str):
        self.call.update(twiml=f'<Response><Say>{text}</Say><Pause length="60"/></Response>')

    def start_session(self):
        self._read_ws()
