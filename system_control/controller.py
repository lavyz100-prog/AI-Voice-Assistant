# system_control/controller.py

# ── Dual-mode imports ─────────────────────────────────────────────────────────
# When imported as a package  (e.g. from system_control import SystemController)
#   → relative imports work fine.
# When run directly from the terminal (python controller.py GET_BATTERY)
#   → relative imports fail, so we fix sys.path and use absolute imports.

import sys as _sys
import os as _os

if __name__ == "__main__":
    # Running directly: patch sys.path so 'system_control' is a proper package
    _voice_assistant_dir = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    if _voice_assistant_dir not in _sys.path:
        _sys.path.insert(0, _voice_assistant_dir)
    from system_control.safety_guard import is_dangerous, get_warning_message
    from system_control import (
        audio_manager,
        power_manager,
        display_manager,
        network_manager,
        app_manager,
        device_info_manager,
        memory_manager,
        datetime_manager,
        screen_manager,
    )
else:
    # Imported as package: use normal relative imports
    from .safety_guard import is_dangerous, get_warning_message
    from . import (
        audio_manager,
        power_manager,
        display_manager,
        network_manager,
        app_manager,
        device_info_manager,
        memory_manager,
        datetime_manager,
        screen_manager,
    )


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

            # ── Audio / Volume ────────────────────────────────────────────
            "ADJUST_VOLUME":            audio_manager.adjust_volume,
            "SET_VOLUME":               audio_manager.set_volume,
            "MUTE_VOLUME":              audio_manager.mute_volume,
            "UNMUTE_VOLUME":            audio_manager.unmute_volume,

            # ── Power Management ──────────────────────────────────────────
            "SYSTEM_SHUTDOWN":          power_manager.shutdown,
            "SYSTEM_RESTART":           power_manager.restart,
            "SYSTEM_SLEEP":             power_manager.sleep,
            "CANCEL_SHUTDOWN":          power_manager.cancel_shutdown,

            # ── Display / Brightness ──────────────────────────────────────
            "SET_BRIGHTNESS":           display_manager.set_brightness,
            "ADJUST_BRIGHTNESS":        display_manager.adjust_brightness,
            "TOGGLE_NIGHT_LIGHT":       display_manager.toggle_night_light,

            # ── Network ───────────────────────────────────────────────────
            "WIFI_ON":                  network_manager.wifi_on,
            "WIFI_OFF":                 network_manager.wifi_off,
            "BLUETOOTH_ON":             network_manager.bluetooth_on,
            "BLUETOOTH_OFF":            network_manager.bluetooth_off,

            # ── Applications ──────────────────────────────────────────────
            "OPEN_APP":                 app_manager.open_app,

            # ── Device Information ────────────────────────────────────────
            "GET_BATTERY":              device_info_manager.get_battery,
            "GET_CPU_USAGE":            device_info_manager.get_cpu_usage,
            "GET_DISK_SPACE":           device_info_manager.get_disk_space,

            # ── Memory ────────────────────────────────────────────────────
            "GET_RAM_USAGE":            memory_manager.get_ram_usage,
            "GET_RAM_DETAILS":          memory_manager.get_ram_details,
            "GET_VIRTUAL_MEMORY":       memory_manager.get_virtual_memory,
            "GET_TOP_MEMORY_PROCESSES": memory_manager.get_top_memory_processes,
            "GET_MEMORY_HEALTH":        memory_manager.get_memory_health,
            "CLEAR_RAM":                memory_manager.clear_ram,

            # ── Date & Time ───────────────────────────────────────────────
            "GET_TIME":                 datetime_manager.get_time,
            "GET_DATE":                 datetime_manager.get_date,
            "GET_DATETIME":             datetime_manager.get_datetime,

            # ── Screen ────────────────────────────────────────────────────
            "TAKE_SCREENSHOT":          screen_manager.take_screenshot,
            "LOCK_SCREEN":              screen_manager.lock_screen,
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


# ─── CLI Runner ───────────────────────────────────────────────────────────────
# Lets you run ANY intent directly:
#   python controller.py GET_BATTERY
#   python controller.py SET_VOLUME percentage=60
#   python controller.py OPEN_APP app_name=calculator
#   python controller.py list        <- shows all intents
#   python controller.py help        <- shows usage
#
# HOW IT WORKS:
#   controller.py uses relative imports (from .safety_guard ...) which only
#   work inside a package. When run directly, we patch sys.path so that the
#   parent folder (voice_assistant/) is on the path, then re-import the
#   whole system_control package properly via absolute import.

if __name__ == "__main__":

    sc = SystemController()

    # ── Helpers ───────────────────────────────────────────────────────────────
    SEP  = "=" * 60
    SEP2 = "-" * 60

    YES = {"yes", "y", "ok", "confirm", "sure"}
    NO  = {"no", "n", "cancel", "skip", "abort"}

    def _ok(msg):   print(f"\n  [ OK ]  {msg}")
    def _fail(msg): print(f"\n  [FAIL]  {msg}")
    def _warn(msg): print(f"\n  [WARN]  {msg}")
    def _info(msg): print(f"\n  [INFO]  {msg}")

    def _confirm(prompt):
        while True:
            reply = input(f"\n  >> {prompt} (yes/no): ").strip().lower()
            if reply in YES: return True
            if reply in NO:  return False
            print("  Please type yes or no.")

    def _run(intent, params, confirmed=False):
        """Execute one intent and display the result."""
        params_str = ", ".join(f"{k}={v!r}" for k, v in params.items()) or "(no params)"
        print(f"\n{SEP}")
        print(f"  Intent  : {intent}")
        print(f"  Params  : {params_str}")
        print(SEP)

        result = sc.execute_task(intent, params, is_confirmed=confirmed)
        status  = result.get("status",  "")
        message = result.get("message", "")
        details = result.get("details", "")

        if status == "SUCCESS":
            _ok(message)
            if details:
                print(f"\n{details}")

        elif status == "REQUIRES_CONFIRMATION":
            _warn(message)
            if _confirm("Execute this dangerous command?"):
                _run(intent, params, confirmed=True)
            else:
                _info("Cancelled — nothing happened.")

        elif status == "ERROR":
            _fail(message)

        elif status == "UNKNOWN_INTENT":
            _fail(message)
            print(f"\n  Available intents:\n  "
                  + "\n  ".join(sorted(sc.intent_map.keys())))
        print()

    def _list_intents():
        """Print every registered intent."""
        print(f"\n{SEP}")
        print(f"  All intents registered in controller.py  ({len(sc.intent_map)} total)")
        print(SEP)
        categories = {}
        for intent in sc.intent_map:
            cat = intent.split("_")[0]
            categories.setdefault(cat, []).append(intent)
        for cat, intents in categories.items():
            print(f"\n  [{cat}]")
            for i in intents:
                print(f"    {i}")
        print()

    def _show_help():
        print("""
  USAGE (run from system_control/ folder):
    python controller.py <INTENT>
    python controller.py <INTENT> key=value key2=value2
    python controller.py list
    python controller.py help

  EXAMPLES:
    python controller.py GET_BATTERY
    python controller.py GET_TIME
    python controller.py GET_DATE
    python controller.py GET_DATETIME
    python controller.py GET_RAM_USAGE
    python controller.py GET_RAM_DETAILS
    python controller.py GET_VIRTUAL_MEMORY
    python controller.py GET_MEMORY_HEALTH
    python controller.py GET_TOP_MEMORY_PROCESSES
    python controller.py GET_CPU_USAGE
    python controller.py GET_DISK_SPACE
    python controller.py GET_DISK_SPACE drive=D
    python controller.py TAKE_SCREENSHOT
    python controller.py MUTE_VOLUME
    python controller.py UNMUTE_VOLUME
    python controller.py SET_VOLUME percentage=70
    python controller.py ADJUST_VOLUME percentage_change=10
    python controller.py ADJUST_VOLUME percentage_change=-10
    python controller.py SET_BRIGHTNESS level=60
    python controller.py ADJUST_BRIGHTNESS change=10
    python controller.py TOGGLE_NIGHT_LIGHT
    python controller.py WIFI_ON
    python controller.py WIFI_OFF
    python controller.py BLUETOOTH_ON
    python controller.py BLUETOOTH_OFF
    python controller.py OPEN_APP app_name=calculator
    python controller.py OPEN_APP app_name=notepad
    python controller.py CANCEL_SHUTDOWN
    python controller.py CLEAR_RAM          [asks for confirmation]
    python controller.py SYSTEM_SLEEP       [asks for confirmation]
    python controller.py SYSTEM_RESTART     [asks for confirmation]
    python controller.py SYSTEM_SHUTDOWN    [asks for confirmation]
    python controller.py LOCK_SCREEN        [asks for confirmation]
    python controller.py list               [show all intents]
""")

    # ── Parse args ────────────────────────────────────────────────────────────
    args = _sys.argv[1:]

    if not args or args[0].lower() in ("help", "--help", "-h"):
        _show_help()
        _sys.exit(0)

    if args[0].lower() in ("list", "--list", "-l"):
        _list_intents()
        _sys.exit(0)

    # Intent name is the first arg (case-insensitive, auto-uppercased)
    intent = args[0].upper()

    # Remaining args are key=value pairs
    params = {}
    for arg in args[1:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            try:
                v = int(v)      # convert numeric values automatically
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass        # keep as string
            params[k.strip()] = v
        else:
            print(f"  [WARN]  Ignoring unrecognised argument: '{arg}'  "
                  f"(use key=value format, e.g. percentage=60)")

    _run(intent, params)
