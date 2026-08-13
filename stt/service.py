import speech_recognition as sr

from .config import STTConfig
from .microphone import Microphone
from .recorder import Recorder
from .recognizer import Recognizer
from .cleaner import TextCleaner


class STT:

    def __init__(self, config=None):

        self.config = config or STTConfig()

        self.recognizer_engine = sr.Recognizer()

        self.microphone = Microphone(
            self.config
        )

        self.recorder = Recorder(
            self.microphone,
            self.recognizer_engine,
            self.config
        )

        self.recognizer = Recognizer(
            self.config
        )

        self.microphone.calibrate(
            self.recognizer_engine
        )

    def listen(self):

        audio = self.recorder.record()

        if audio is None:
            return None

        text = self.recognizer.recognize(
            audio
        )

        return TextCleaner.clean(text)