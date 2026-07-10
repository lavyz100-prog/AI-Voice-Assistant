import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 180)      # Speed
engine.setProperty("volume", 1.0)    # Volume (0.0 - 1.0)

text = input("Enter text: ")

engine.say(text)
engine.runAndWait()