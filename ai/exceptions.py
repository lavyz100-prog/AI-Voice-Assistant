class AIError(Exception):
    """Base AI exception."""


class AIConfigError(AIError):
    """Missing or invalid configuration (e.g. API key)."""


class AIResponseError(AIError):
    """Failed to get a response from the AI."""
