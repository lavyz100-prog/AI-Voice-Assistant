import speech_recognition as sr

from .audio import AudioProcessor
from .exceptions import RecognitionError


class Recognizer:

    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()

    def recognize(self, audio):

        if not AudioProcessor.is_valid(audio):
            return None

        try:

            text = self.recognizer.recognize_google(
                audio,
                language=self.config.language
            )

            return text

        except sr.UnknownValueError:
            return None

        except sr.RequestError as e:
            raise RecognitionError(
                f"Recognition service failed: {e}"
            )