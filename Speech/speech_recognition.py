import speech_recognition as sr
import re
r = sr.Recognizer()
mic = sr.Microphone()
with mic as source:
    #r.adjust_for_ambient_noise(source)
    audio = r.listen(source) 

mov = r.recognize_google(audio)
pos = re.findall("[A-H][1-8]", mov)

print(mov)
