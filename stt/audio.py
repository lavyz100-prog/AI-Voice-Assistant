class AudioProcessor:

    @staticmethod
    def is_valid(audio):

        if audio is None:
            return False

        try:
            data = audio.get_raw_data()

            return len(data) > 0

        except Exception:
            return False