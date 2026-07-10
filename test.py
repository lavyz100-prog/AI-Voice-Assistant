import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak...")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio)
    print(text)
except Exception as e:
    print(e)