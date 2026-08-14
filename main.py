from stt import STT


stt = STT()


try:

    while True:

        text = stt.listen()

        if not text:
            continue

        print("You:", text)

        if text.lower() == "exit":
            break

except KeyboardInterrupt:

    print("\nStopping...")