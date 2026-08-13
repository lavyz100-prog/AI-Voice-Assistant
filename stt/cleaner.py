import re


class TextCleaner:

    @staticmethod
    def clean(text):

        if not text:
            return None

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        if not text:
            return None

        return text