# system_control/safety_guard.py

# Intents that require explicit user confirmation before execution.
DANGEROUS_INTENTS = {
    # Power — irreversible system state changes
    "SYSTEM_SHUTDOWN":    "This will shut down the computer.",
    "SYSTEM_RESTART":     "This will restart the computer.",
    "SYSTEM_SLEEP":       "This will put the computer to sleep.",

    # Screen — locks the user out immediately
    "LOCK_SCREEN":        "This will lock the screen immediately.",

    # Memory — modifies process memory state across the system
    "CLEAR_RAM":          "This will trim working sets of all running processes.",
}


def is_dangerous(intent_name: str) -> bool:
    """Return True if the intent requires a confirmation step."""
    return intent_name in DANGEROUS_INTENTS


def get_warning_message(intent_name: str, parameters: dict) -> str:
    """Build a human-readable warning that the assistant should speak aloud."""
    base_warning = DANGEROUS_INTENTS.get(intent_name, "This is a sensitive operation.")
    return (
        f"Warning: {base_warning} "
        f"Say 'yes' or 'confirm' to proceed."
    )
