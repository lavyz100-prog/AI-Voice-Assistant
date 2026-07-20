# system_control/safety_guard.py

# Intents that require explicit user confirmation before execution.
DANGEROUS_INTENTS = {
    "SYSTEM_SHUTDOWN":    "This will shut down the computer.",
    "SYSTEM_RESTART":     "This will restart the computer.",
    "SYSTEM_SLEEP":       "This will put the computer to sleep.",
}


def is_dangerous(intent_name: str) -> bool:
    """Return True if the intent requires a confirmation step."""
    return intent_name in DANGEROUS_INTENTS


def get_warning_message(intent_name: str, parameters: dict) -> str:
    """Build a human-readable warning that the assistant should speak aloud."""
    base_warning = DANGEROUS_INTENTS.get(intent_name, "This is a dangerous task.")
    return (
        f"Warning: {base_warning} "
        f"Say 'yes' or 'confirm' to proceed."
    )
