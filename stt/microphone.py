import speech_recognition as sr

from .config import STTConfig
from .exceptions import MicrophoneError


class Microphone:

    def __init__(self, config: STTConfig):
        self.config = config

        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            raise MicrophoneError(
                f"Failed to initialize microphone: {e}"
            )

    def calibrate(self, recognizer):

        print("Calibrating microphone...")
        print("Please remain silent...")

        with self.microphone as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=self.config.ambient_duration
            )

        print(
            "Energy threshold:",
            recognizer.energy_threshold
        )

        print("Microphone ready.")

    def get_source(self):
        return self.microphone