from .states import STTState


class STTController:

    def __init__(self, stt):

        self.stt = stt

        self.state = STTState.IDLE

        self.running = False

    def start(self):

        if self.running:
            return None

        self.running = True
        self.state = STTState.LISTENING

        try:

            text = self.stt.listen()

            self.state = STTState.IDLE

            return text

        except Exception as e:

            self.state = STTState.ERROR

            print(f"STT error: {e}")

            return None

        finally:

            self.running = False

    def stop(self):

        self.running = False
        self.state = STTState.STOPPED

    def is_running(self):

        return self.running

    def get_state(self):

        return self.state