from abc import ABC, abstractmethod
from typing import Optional
import os
import tempfile
import subprocess

from gtts import gTTS
import pyaudio
import wave


class TTSClient(ABC):
    @abstractmethod
    def text_to_mp3(self, text: str, output_fn: Optional[str] = None) -> str:
        pass

    def play_text(self, text: str) -> str:
        tmp_mp3 = self.text_to_mp3(text)
        tmp_wav = tmp_mp3.replace(".mp3", ".wav")
        subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", tmp_mp3, tmp_wav])

        wf = wave.open(tmp_wav, "rb")
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
        )

        data = wf.readframes(1024)
        while data != b"":
            stream.write(data)
            data = wf.readframes(1024)

        stream.close()
        audio.terminate()

    def get_duration(self, audio_fn: str) -> float:
        popen = subprocess.Popen(
            ["ffprobe", "-hide_banner", "-loglevel", "error", "-show_entries", "format=duration", "-i", audio_fn],
            stdout=subprocess.PIPE,
        )
        popen.wait()
        output = popen.stdout.read().decode("utf-8")
        duration = float(output.split("=")[1].replace("\r\n", "\n").split("\n")[0])
        return duration


class GoogleTTS(TTSClient):
    def text_to_mp3(self, text: str, output_fn: Optional[str] = None) -> str:
        tmp_fn = output_fn or os.path.join(tempfile.mkdtemp(), "tts.mp3")
        tts = gTTS(text, lang="en")
        tts.save(tmp_fn)
        return tmp_fn
