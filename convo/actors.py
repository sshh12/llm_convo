from typing import List
from abc import ABC, abstractmethod

from convo.audio_input import WhisperMicrophone
from convo.audio_output import TTSSpeaker
from convo.openai_io import OpenAIChatCompletion


class ChatAgent(ABC):
    @abstractmethod
    def get_response(self, transcript: List[str]) -> str:
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
    def __init__(self):
        self.openai_chat = OpenAIChatCompletion()

    def get_response(self, transcript: List[str]) -> str:
        if len(transcript) > 0:
            response = self.openai_chat.get_response(transcript)
        else:
            response = "Generic"
        return response
