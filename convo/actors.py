from typing import List, Optional
from abc import ABC, abstractmethod

from convo.audio_input import WhisperMicrophone
from convo.audio_output import TTSSpeaker
from convo.openai_io import OpenAIChatCompletion
from convo.twilio_io import TwilioCallSession


class ChatAgent(ABC):
    @abstractmethod
    def get_response(self, transcript: List[str]) -> str:
        pass

    def start(self):
        pass


class MicrophoneInSpeakerTTSOut(ChatAgent):
    def __init__(self):
        self.mic = WhisperMicrophone()
        self.speaker = TTSSpeaker()

    def get_response(self, transcript: List[str]) -> str:
        if len(transcript) > 0:
            self.speaker.play(transcript[-1])
        return self.mic.get_transcription()


class TerminalInPrintOut(ChatAgent):
    def get_response(self, transcript: List[str]) -> str:
        if len(transcript) > 0:
            print(transcript[-1])
        return input(" response > ")


class OpenAIChat(ChatAgent):
    def __init__(self, init_phrase: Optional[str] = None):
        self.openai_chat = OpenAIChatCompletion()
        self.init_phrase = init_phrase

    def get_response(self, transcript: List[str]) -> str:
        if len(transcript) > 0:
            response = self.openai_chat.get_response(transcript)
        else:
            response = self.init_phrase
        return response


class TwilioCaller(ChatAgent):
    def __init__(self, session: TwilioCallSession):
        self.session = session

    def get_response(self, transcript: List[str]) -> str:
        if len(transcript) > 0:
            self.session.say(transcript[-1])
        resp = self.session.sst_stream.get_transcription()
        self.session.say("Ok")
        return resp
