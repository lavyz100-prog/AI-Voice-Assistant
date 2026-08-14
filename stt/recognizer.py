import speech_recognition as sr

from .exceptions import RecognitionError


class Recognizer:

    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()

    def recognize(self, audio):

        # Validate audio has actual data
        if audio is None:
            return None

        try:
            if len(audio.get_raw_data()) == 0:
                return None
        except Exception:
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