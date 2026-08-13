from stt import STT, STTController


stt = STT()

controller = STTController(stt)


try:

    while True:

        text = controller.start()

        if not text:
            continue

        print("You:", text)

        if text.lower() == "exit":
            break

except KeyboardInterrupt:

    print("\nStopping...")

finally:

    controller.stop()