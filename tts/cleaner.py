import re


class MarkdownCleaner:
    """Strip markdown formatting so text sounds natural when spoken aloud."""

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return text

        # Remove bold/italic (**text**, *text*, __text__, _text_)
        text = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', text)
        text = re.sub(r'_{1,3}(.+?)_{1,3}', r'\1', text)

        # Remove inline code (`code`)
        text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)

        # Remove headings (# Heading)
        text = re.sub(r'^\s*#{1,6}\s+', '', text, flags=re.MULTILINE)

        # Replace numbered list markers with just the text
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # Replace bullet list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)

        # Collapse multiple blank lines into one
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()
