class STTError(Exception):
    """Base STT exception."""


class MicrophoneError(STTError):
    """Microphone-related error."""


class RecordingError(STTError):
    """Audio recording error."""


class RecognitionError(STTError):
    """Speech recognition error."""