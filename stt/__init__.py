from .config import STTConfig
from .service import STT
from .exceptions import STTError, MicrophoneError, RecordingError, RecognitionError


__all__ = [
    "STT",
    "STTConfig",
    "STTError",
    "MicrophoneError",
    "RecordingError",
    "RecognitionError",
]