from .config import TTSConfig
from .engine import TTSEngine


class TTS:

    def __init__(self, config=None):
        self.config = config or TTSConfig()
        self.engine = TTSEngine(self.config)

    def speak(self, text):
        if not text:
            return

        text = str(text).strip()

        if text:
            self.engine.speak(text)

    def stop(self):
        self.engine.stop()