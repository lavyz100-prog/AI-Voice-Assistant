from speech_to_text import record_audio, transcribe
from text_to_speech import speak
from llm import ask_ai


def main():
    print("AI Desktop Assistant (Groq) — say 'exit' to quit")
    try:
        while True:
            wav = record_audio()
            if not wav:
                # Recording failed; continue listening
                continue

            user_text = transcribe(wav)
            if not user_text:
                continue

            if "exit" in user_text.lower():
                speak("Goodbye!")
                break

            reply = ask_ai(user_text)
            if not reply:
                reply = "Sorry, I couldn't generate a reply."

            spoken = speak(reply)
            if isinstance(spoken, str) and spoken.startswith("Error:"):
                print(spoken)

    except KeyboardInterrupt:
        print("Interrupted by user. Exiting.")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()