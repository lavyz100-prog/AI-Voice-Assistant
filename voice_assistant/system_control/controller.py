# system_control/controller.py

from .safety_guard import is_dangerous, get_warning_message
from . import audio_manager, power_manager


class SystemController:
    """
    Central router for the system_control module.
    Receives an intent + parameters from the NLP layer,
    enforces safety checks, and dispatches to the correct manager.
    """

    def __init__(self):
        # ─── Intent → Execution Function Map ───────────────────────────────
        # Each key is the NLP-layer intent name (uppercase string).
        # Each value is the Python callable that performs the real work.
        self.intent_map = {
            # Audio / volume
            "ADJUST_VOLUME":      audio_manager.adjust_volume,
            "SET_VOLUME":         audio_manager.set_volume,
            "MUTE_VOLUME":        audio_manager.mute_volume,
            "UNMUTE_VOLUME":      audio_manager.unmute_volume,

            # Power management
            "SYSTEM_SHUTDOWN":    power_manager.shutdown,
            "SYSTEM_RESTART":     power_manager.restart,
            "SYSTEM_SLEEP":       power_manager.sleep,
            "CANCEL_SHUTDOWN":    power_manager.cancel_shutdown,
        }

    # ──────────────────────────────────────────────────────────────────────
    def execute_task(
        self,
        intent: str,
        parameters: dict,
        is_confirmed: bool = False,
    ) -> dict:
        """
        Public entry point called by main.py.

        Parameters
        ----------
        intent       : NLP intent name, e.g. "ADJUST_VOLUME"
        parameters   : Keyword arguments forwarded to the execution function.
        is_confirmed : True when the user has already spoken a confirmation word.

        Returns
        -------
        dict with keys:
          status  → "SUCCESS" | "ERROR" | "REQUIRES_CONFIRMATION" | "UNKNOWN_INTENT"
          message → Human-readable string for the TTS layer to speak.
        """
        # 1. Guard against completely unknown intents
        if intent not in self.intent_map:
            return {
                "status": "UNKNOWN_INTENT",
                "message": f"I don't know how to handle the intent '{intent}'.",
            }

        # 2. Safety gate — dangerous intents halt until user confirms
        if is_dangerous(intent) and not is_confirmed:
            warning = get_warning_message(intent, parameters)
            return {
                "status": "REQUIRES_CONFIRMATION",
                "message": warning,
                # Echo back the pending intent so main.py can resume it
                "pending_intent": intent,
                "pending_parameters": parameters,
            }

        # 3. Execute — either the intent is safe, or confirmation was given
        execution_function = self.intent_map[intent]
        try:
            result = execution_function(**parameters)
        except TypeError as e:
            # Parameter mismatch between NLP output and function signature
            result = {
                "status": "ERROR",
                "message": f"Parameter error for intent '{intent}': {e}",
            }

        return result
