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


# ─── Stub: replace with your real NLP / LLM intent parser ────────────────────────
def parse_intent(transcript: str) -> dict:
    """
    Maps a raw transcript to an intent dict.
    Returns:
        {
          "intent":     str,   e.g. "ADJUST_VOLUME"
          "parameters": dict,  e.g. {"percentage_change": 10}
        }
    Example keyword map — replace with spaCy / GPT / Rasa output.
    """
    t = transcript.lower()

    # ── Volume ────────────────────────────────────────────────────────────
    if "volume up" in t or "increase volume" in t:
        return {"intent": "ADJUST_VOLUME", "parameters": {"percentage_change": 10}}
    if "volume down" in t or "decrease volume" in t:
        return {"intent": "ADJUST_VOLUME", "parameters": {"percentage_change": -10}}
    if "mute" in t and "unmute" not in t:
        return {"intent": "MUTE_VOLUME", "parameters": {}}
    if "unmute" in t:
        return {"intent": "UNMUTE_VOLUME", "parameters": {}}

    # ── Power ─────────────────────────────────────────────────────────────
    if "shut down" in t or "shutdown" in t:
        return {"intent": "SYSTEM_SHUTDOWN", "parameters": {"delay_seconds": 10}}
    if "restart" in t or "reboot" in t:
        return {"intent": "SYSTEM_RESTART", "parameters": {"delay_seconds": 10}}
    if "sleep" in t:
        return {"intent": "SYSTEM_SLEEP", "parameters": {}}
    if "cancel shutdown" in t or "abort shutdown" in t:
        return {"intent": "CANCEL_SHUTDOWN", "parameters": {}}

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
