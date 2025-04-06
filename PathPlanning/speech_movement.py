import speech_recognition as sr
import re

r = sr.Recognizer()
mic = sr.Microphone()

def detect_moves():
    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("Talk (say position of piece and movement piece like 'e2 to e4 or e2e4') or robot")
        audio = r.listen(source, phrase_time_limit=20)

    try:
        mov = r.recognize_google(audio)
        print(f"Recognized Speech: {mov}")
        if (mov == "robots"):
            return mov
        else:       
            moves = re.findall(r"[a-hA-H][1-8](?: to [a-hA-H][1-8])?", mov)        
            moves = [move.replace(" to ", "") if " to " in move else move for move in moves]
            moves = [move.lower() for move in moves]
            combined_moves = "".join(moves)
            return combined_moves
    
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError:
        print("Could not request results, check your internet connection.")
        return ""
