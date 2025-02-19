import speech_recognition as sr
import re

r = sr.Recognizer()
mic = sr.Microphone()

# Function to detect multiple moves
def detect_moves(audio):
    try:
        mov = r.recognize_google(audio)
        print(f"Recognized text: {mov}")
        
        # Updated regex to handle both with and without "to"
        moves = re.findall(r"[a-hA-H][1-8](?: to [a-hA-H][1-8])?", mov)
        
        # Process the moves: if 'to' exists, remove it; otherwise, keep the move as is
        moves = [move.replace(" to ", "") if " to " in move else move for move in moves]
        
        # Normalize the moves to lowercase
        moves = [move.lower() for move in moves]
        
        # Combine the moves into a single string
        combined_moves = "".join(moves)
        
        return combined_moves
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError:
        print("Could not request results, check your internet connection.")
        return ""

with mic as source:
    r.adjust_for_ambient_noise(source)
    print("Talk (you can say multiple moves like 'e2 to e4 or e2e4')")

    # Listen for the user's speech (up to 10 seconds)
    audio = r.listen(source, phrase_time_limit=10)

# Process the audio and detect all moves
combined_moves = detect_moves(audio)

# Output the combined moves
if combined_moves:
    print(f"Detected moves: {combined_moves}")
else:
    print("No valid moves detected.")
