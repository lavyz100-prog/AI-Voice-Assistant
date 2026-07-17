import speech_recognition as sr
import pyttsx3
from groq import Groq
import time

# ==========================
# Replace with your NEW API KEY
# ==========================

import os

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

recognizer = sr.Recognizer()

# Conversation memory
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI voice assistant. Keep responses concise unless the user asks for details."
    }
]


def speak(text):
    """Speak using a fresh engine every time (works better on macOS)."""
    print("\nAI:", text)

    engine = pyttsx3.init()

    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)

    voices = engine.getProperty("voices")
    if voices:
        engine.setProperty("voice", voices[108].id)

    engine.say(text)
    engine.runAndWait()
    engine.stop()

    time.sleep(0.3)


def listen():
    with sr.Microphone() as source:

        print("\nListening...")

        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=15
            )

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print("You:", text)
        return text

    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand.")
        return None

    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None


def ask_ai(question):

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=512
    )

    answer = response.choices[0].message.content

    messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return answer


def main():

    speak("Hello. How can I help you today?")

    while True:

        question = listen()

        if question is None:
            continue

        EXIT_COMMANDS = {
            "exit",
            "quit",
            "close",
            "close program",
            "close application",
            "shutdown",
            "stop",
            "goodbye",
            "bye",
            "terminate"
        }

        if any(command in question.lower() for command in EXIT_COMMANDS):
            speak("Goodbye. Shutting down.")
            break

        try:
            answer = ask_ai(question)
            speak(answer)

        except Exception as e:
            print("Error:", e)
            speak("Sorry, something went wrong.")


if __name__ == "__main__":
    main()