import io
import os
import tempfile
import queue
import functools

from pydub import AudioSegment
import speech_recognition as sr
import whisper


@functools.cache
def get_wisper():
    return whisper.load_model("large")


class WhisperMicrophone:
    def __init__(self):
        self.audio_model = get_wisper()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = False

    def get_transcription(self) -> str:
        with sr.Microphone(sample_rate=16000) as source:
            print("Waiting for mic...")
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = os.path.join(tmp, "mic.wav")
                audio = self.recognizer.listen(source)
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                audio_clip.export(tmp_path, format="wav")
                result = self.audio_model.transcribe(tmp_path, language="english")
            predicted_text = result["text"]
        return predicted_text


class _TwilioSource(sr.AudioSource):
    def __init__(self, stream):
        self.stream = stream
        self.CHUNK = 1024
        self.SAMPLE_RATE = 8000
        self.SAMPLE_WIDTH = 2

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class _QueueStream:
    def __init__(self, q: queue.Queue):
        self.q = q

    def read(self, chunk: int) -> bytes:
        return self.q.get()


class WhisperTwilioStream:
    def __init__(self):
        self.audio_model = get_wisper()
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 500
        self.recognizer.pause_threshold = 1.5
        self.recognizer.dynamic_energy_threshold = False
        self.stream = None

    def get_transcription(self) -> str:
        self.stream = queue.Queue(maxsize=-1)
        with _TwilioSource(_QueueStream(self.stream)) as source:
            print("Waiting for twilio...")
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = os.path.join(tmp, "mic.wav")
                audio = self.recognizer.listen(source)
                data = io.BytesIO(audio.get_wav_data())
                audio_clip = AudioSegment.from_file(data)
                audio_clip.export(tmp_path, format="wav")
                result = self.audio_model.transcribe(tmp_path, language="english")
            predicted_text = result["text"]
        return predicted_text
