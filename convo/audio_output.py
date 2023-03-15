import os
import tempfile
import subprocess

from gtts import gTTS
import pyaudio
import wave


class TTSSpeaker:
    def __init__(self):
        self.chunk_size = 1024

    def play(self, text: str):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            tmp_mp3 = os.path.join(tmp, "tts.mp3")
            tmp_wav = os.path.join(tmp, "tts.wav")
            tts = gTTS(text, lang="en")
            tts.save(tmp_mp3)
            subprocess.call(["ffmpeg", "-y", "-i", tmp_mp3, tmp_wav])

            wf = wave.open(tmp_wav, "rb")
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
            )

            data = wf.readframes(self.chunk_size)
            while data != b"":
                stream.write(data)
                data = wf.readframes(self.chunk_size)

            stream.close()
            audio.terminate()
