# voice_assistant/main.py
"""
Main Orchestrator Loop
======================
Connects three layers:
  1. STT  — Speech-to-Text   (stubbed; swap in your real implementation)
  2. NLP  — Intent extraction (stubbed; swap in your real implementation)
  3. SC   — System Control    (fully wired to system_control/)

Confirmation Flow
-----------------
When a dangerous intent arrives, the assistant:
  a) Speaks the warning  →  "Warning: This will shut down the computer…"
  b) Listens for "yes" / "confirm" / "ok"
  c) Re-executes the same intent with is_confirmed=True
  d) If the user says anything else → intent is cancelled.
"""

import re
import time
from system_control import SystemController

# ─── Stub: replace with your real STT engine (e.g. Whisper / SpeechRecognition) ──
def listen_for_speech() -> str:
    """
    Captures audio from the microphone and returns a transcript string.
    Currently uses console input so the project runs without a microphone.
    """
    raw = input("\n🎤  You: ").strip()
    return raw


# ─── NLP Intent Parser ────────────────────────────────────────────────────────
def _extract_number(text: str, default: int = None) -> int | None:
    """Extract the first integer found in text, or return default."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else default


def _extract_drive(text: str, default: str = "C") -> str:
    """Extract a drive letter (e.g. 'D drive') from text."""
    match = re.search(r"\b([a-zA-Z])\s*(?:drive|disk|:\s)", text)
    return match.group(1).upper() if match else default


def parse_intent(transcript: str) -> dict:
    """
    Maps a raw transcript to an intent dict.
    Returns:
        {
          "intent":     str,   e.g. "ADJUST_VOLUME"
          "parameters": dict,  e.g. {"percentage_change": 10}
        }
    Keyword-based NLP stub — replace with spaCy / GPT / Rasa output.
    """
    t = transcript.lower()

    # ── Volume ────────────────────────────────────────────────────────────
    if "volume up" in t or "increase volume" in t or "raise volume" in t:
        pct = _extract_number(t, 10)
        return {"intent": "ADJUST_VOLUME", "parameters": {"percentage_change": pct}}
    if "volume down" in t or "decrease volume" in t or "lower volume" in t:
        pct = _extract_number(t, 10)
        return {"intent": "ADJUST_VOLUME", "parameters": {"percentage_change": -pct}}
    if ("set volume" in t or "volume to" in t) and re.search(r"\d+", t):
        pct = _extract_number(t, 50)
        return {"intent": "SET_VOLUME", "parameters": {"percentage": pct}}
    if "mute" in t and "unmute" not in t:
        return {"intent": "MUTE_VOLUME", "parameters": {}}
    if "unmute" in t:
        return {"intent": "UNMUTE_VOLUME", "parameters": {}}

    # ── Power ─────────────────────────────────────────────────────────────
    if "shut down" in t or "shutdown" in t or "power off" in t or "turn off" in t:
        return {"intent": "SYSTEM_SHUTDOWN", "parameters": {"delay_seconds": 10}}
    if "restart" in t or "reboot" in t:
        return {"intent": "SYSTEM_RESTART", "parameters": {"delay_seconds": 10}}
    if "sleep" in t and "night" not in t:
        return {"intent": "SYSTEM_SLEEP", "parameters": {}}
    if "cancel shutdown" in t or "abort shutdown" in t:
        return {"intent": "CANCEL_SHUTDOWN", "parameters": {}}

    # ── Display / Brightness ──────────────────────────────────────────────
    if ("set brightness" in t or "brightness to" in t) and re.search(r"\d+", t):
        level = _extract_number(t, 70)
        return {"intent": "SET_BRIGHTNESS", "parameters": {"level": level}}
    if "increase brightness" in t or "brightness up" in t or "brighter" in t:
        change = _extract_number(t, 10)
        return {"intent": "ADJUST_BRIGHTNESS", "parameters": {"change": change}}
    if "decrease brightness" in t or "brightness down" in t or "dimmer" in t or "dim" in t:
        change = _extract_number(t, 10)
        return {"intent": "ADJUST_BRIGHTNESS", "parameters": {"change": -change}}
    if "night light" in t or "night mode" in t or "blue light" in t:
        return {"intent": "TOGGLE_NIGHT_LIGHT", "parameters": {}}

    # ── Network ───────────────────────────────────────────────────────────
    if "wifi" in t or "wi-fi" in t or "wireless" in t:
        if any(w in t for w in ("on", "enable", "turn on", "connect")):
            return {"intent": "WIFI_ON", "parameters": {}}
        if any(w in t for w in ("off", "disable", "turn off", "disconnect")):
            return {"intent": "WIFI_OFF", "parameters": {}}
    if "bluetooth" in t:
        if any(w in t for w in ("on", "enable", "turn on")):
            return {"intent": "BLUETOOTH_ON", "parameters": {}}
        if any(w in t for w in ("off", "disable", "turn off")):
            return {"intent": "BLUETOOTH_OFF", "parameters": {}}

    # ── Applications ──────────────────────────────────────────────────────
    if "open" in t or "launch" in t or "start" in t:
        _APP_KEYWORDS = {
            "task manager": "task manager",
            "taskmgr": "task manager",
            "settings": "settings",
            "control panel": "control panel",
            "notepad": "notepad",
            "calculator": "calculator",
            "calc": "calculator",
            "file explorer": "file explorer",
            "explorer": "file explorer",
            "chrome": "chrome",
            "edge": "edge",
            "firefox": "firefox",
            "vs code": "vs code",
            "visual studio code": "vs code",
            "command prompt": "command prompt",
            "cmd": "cmd",
            "powershell": "powershell",
            "paint": "paint",
            "notepad++": "notepad++",
        }
        for kw, app_name in _APP_KEYWORDS.items():
            if kw in t:
                return {"intent": "OPEN_APP", "parameters": {"app_name": app_name}}

    # ── Device Information ────────────────────────────────────────────────
    if "battery" in t:
        return {"intent": "GET_BATTERY", "parameters": {}}
    if "cpu" in t or "processor" in t or "cpu usage" in t:
        return {"intent": "GET_CPU_USAGE", "parameters": {}}
    if "disk space" in t or "storage" in t or "free space" in t or "hard drive space" in t:
        drive = _extract_drive(t)
        return {"intent": "GET_DISK_SPACE", "parameters": {"drive": drive}}

    # ── Memory ────────────────────────────────────────────────────────────
    if "virtual memory" in t or "swap" in t or "page file" in t:
        return {"intent": "GET_VIRTUAL_MEMORY", "parameters": {}}
    if ("top" in t or "which" in t or "most" in t) and ("memory" in t or "ram" in t):
        return {"intent": "GET_TOP_MEMORY_PROCESSES", "parameters": {"top_n": 5}}
    if "memory health" in t or ("memory" in t and ("health" in t or "okay" in t or "ok" in t)):
        return {"intent": "GET_MEMORY_HEALTH", "parameters": {}}
    if "clear" in t and ("ram" in t or "memory" in t):
        return {"intent": "CLEAR_RAM", "parameters": {}}
    if "free" in t and ("ram" in t or "memory" in t):
        return {"intent": "CLEAR_RAM", "parameters": {}}
    if "release" in t and "memory" in t:
        return {"intent": "CLEAR_RAM", "parameters": {}}
    if "ram detail" in t or "memory detail" in t or "memory breakdown" in t:
        return {"intent": "GET_RAM_DETAILS", "parameters": {}}
    if "ram" in t or ("memory" in t and "available" in t) or ("how much" in t and "ram" in t):
        return {"intent": "GET_RAM_USAGE", "parameters": {}}

    # ── Date & Time ───────────────────────────────────────────────────────
    if ("time" in t and "date" in t) or "date and time" in t:
        return {"intent": "GET_DATETIME", "parameters": {}}
    if "time" in t and any(w in t for w in ("what", "tell", "current", "now")):
        return {"intent": "GET_TIME", "parameters": {}}
    if "date" in t and any(w in t for w in ("what", "tell", "today", "current")):
        return {"intent": "GET_DATE", "parameters": {}}
    if "what day" in t:
        return {"intent": "GET_DATE", "parameters": {}}

    # ── Screen ────────────────────────────────────────────────────────────
    if "screenshot" in t or "capture screen" in t or "take a screen" in t:
        return {"intent": "TAKE_SCREENSHOT", "parameters": {}}
    if "lock" in t and ("screen" in t or "computer" in t or "pc" in t or "laptop" in t):
        return {"intent": "LOCK_SCREEN", "parameters": {}}

    # ── Unknown ───────────────────────────────────────────────────────────
    return {"intent": "UNKNOWN", "parameters": {}}


# ─── Stub: replace with your real TTS engine (e.g. pyttsx3 / gTTS / ElevenLabs) ─
def speak(text: str) -> None:
    """
    Converts text to speech output.
    Currently prints to the console — swap in pyttsx3 / gTTS as needed.
    """
    print(f"\n🔊  Assistant: {text}")


# ─── Confirmation helper ──────────────────────────────────────────────────────────
CONFIRMATION_WORDS = {"yes", "yeah", "yep", "confirm", "ok", "okay", "do it", "sure"}
CANCELLATION_WORDS = {"no", "nope", "cancel", "stop", "abort", "never mind"}


def ask_for_confirmation() -> bool:
    """
    Listens for a yes/no reply and returns True if the user confirmed.
    """
    reply = listen_for_speech().lower().strip()
    if any(word in reply for word in CONFIRMATION_WORDS):
        return True
    if any(word in reply for word in CANCELLATION_WORDS):
        return False
    speak("I didn't catch that. Please say 'yes' to confirm or 'no' to cancel.")
    # Give the user one more chance
    reply = listen_for_speech().lower().strip()
    return any(word in reply for word in CONFIRMATION_WORDS)


# ─── Main Loop ───────────────────────────────────────────────────────────────────
def main():
    controller = SystemController()
    speak("Hello! I'm your voice assistant. How can I help you today?")
    speak("(Type your command and press Enter — or say 'exit' to quit.)")

    while True:
        # ── Step 1: Listen ────────────────────────────────────────────────
        transcript = listen_for_speech()

        if not transcript:
            continue

        if transcript.lower() in {"exit", "quit", "bye", "goodbye"}:
            speak("Goodbye! Have a great day.")
            break

        # ── Step 2: Parse Intent ──────────────────────────────────────────
        parsed = parse_intent(transcript)
        intent = parsed["intent"]
        parameters = parsed["parameters"]

        if intent == "UNKNOWN":
            speak("Sorry, I didn't understand that command.")
            continue

        # ── Step 3: First Execution Attempt ───────────────────────────────
        result = controller.execute_task(intent, parameters, is_confirmed=False)

        # ── Step 4: Handle Response Status ───────────────────────────────
        if result["status"] == "REQUIRES_CONFIRMATION":
            # Speak the warning and wait for user to confirm
            speak(result["message"])
            confirmed = ask_for_confirmation()

            if confirmed:
                # Re-run with confirmation flag
                result = controller.execute_task(
                    result["pending_intent"],
                    result["pending_parameters"],
                    is_confirmed=True,
                )
                speak(result.get("message", "Task completed."))
            else:
                speak("Okay, I've cancelled that. What else can I do for you?")

        elif result["status"] == "SUCCESS":
            speak(result["message"])

        elif result["status"] == "ERROR":
            speak(f"Something went wrong: {result['message']}")

        elif result["status"] == "UNKNOWN_INTENT":
            speak(result["message"])

        # Small pause before listening again
        time.sleep(0.3)


if __name__ == "__main__":
    main()
