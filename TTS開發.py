from gtts import gTTS
from io import BytesIO
import pyaudio

pyAudio = pyaudio.PyAudio()

tts = gTTS("[Python]如何Text to Speech: pyttsx3, gTTS", lang="zh-TW")
f = BytesIO()
a = tts.write_to_fp(f)


tts.save("hello.mp3")
