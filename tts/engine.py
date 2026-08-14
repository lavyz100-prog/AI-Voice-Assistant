import pyttsx3


class TTSEngine:

    def __init__(self, config):
        self.config = config
        self.engine = self._create_engine()

    def _create_engine(self):
        engine = pyttsx3.init()

        engine.setProperty("rate", self.config.rate)
        engine.setProperty("volume", self.config.volume)

        if self.config.voice:
            engine.setProperty("voice", self.config.voice)

        return engine

    def speak(self, text):
        print("TTS:", text)

        self.engine.say(text)
        self.engine.runAndWait()

        # Recreate engine for the next utterance
        self.engine.stop()
        self.engine = self._create_engine()

    def stop(self):
        self.engine.stop()