from stt import STT, STTConfig
stt = STT(STTConfig(language="en-US", timeout=8))
text = stt.listen()   # str | None
print("STT:", text)
from tts import TTS, TTSConfig
tts = TTS(TTSConfig(rate=150))
tts.speak("Hello!")
tts.speak("This is a test of the text-to-speech system.")
