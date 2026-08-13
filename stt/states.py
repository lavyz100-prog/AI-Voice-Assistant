from enum import Enum


class STTState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    STOPPED = "stopped"
    ERROR = "error"