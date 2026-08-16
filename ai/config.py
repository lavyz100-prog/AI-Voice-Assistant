from dataclasses import dataclass


@dataclass
class AIConfig:
    model: str = "openrouter/free"
    system_prompt: str = (
        "You are a helpful AI voice assistant. "
        "Give short, natural responses suitable for speech."
    )