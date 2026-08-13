from dataclasses import dataclass


@dataclass
class STTConfig:

    language: str = "en-IN"

    timeout: float = 5
    phrase_time_limit: float = 10

    # Silence required to end speech
    pause_threshold: float = 0.8

    # Silence around speech
    non_speaking_duration: float = 0.5

    # Microphone calibration
    ambient_duration: float = 2