import speech_recognition as sr

from .exceptions import RecordingError


class Recorder:

    def __init__(self, microphone, recognizer, config):
        self.microphone = microphone
        self.recognizer = recognizer
        self.config = config

    def record(self):

        try:

            with self.microphone.get_source() as source:

                print("Listening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=self.config.timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )

                print("Speech ended.")

                return audio

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

        except Exception as e:
            raise RecordingError(
                f"Recording failed: {e}"
            )