from stt import STT
from tts import TTS
from ai import AI


stt = STT()
tts = TTS()
ai = AI()


print("AI Voice Assistant ready. Say 'exit' to quit.\n")


try:

    while True:

        # 1. Listen for user speech → text
        user_text = stt.listen()

        if not user_text:
            continue

        print(f"You: {user_text}")

        if user_text.lower() == "exit":
            tts.speak("Goodbye!")
            break

        # 2. Send text to AI → get response
        response = ai.chat(user_text)

        if not response:
            continue

        print(f"AI: {response}")

        # 3. Speak the AI response → TTS output
        tts.speak(response)

except KeyboardInterrupt:

    print("\nStopping...")