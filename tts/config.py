from dataclasses import dataclass


@dataclass
class TTSConfig:
    rate: int = 170
    volume: float = 1.0
    voice: str | None = None