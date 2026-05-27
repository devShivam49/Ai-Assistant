from datetime import datetime
from core.listen import listen
from core.speak import speak

FILE = "data/day_summary.txt"

def write_summary():
    speak("Tell me about your day.")
    txt = listen()
    if txt:
        with open(FILE, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]: {txt}\n")
        speak("Got it. Noted down.")
    else:
        speak("Didn't catch that.")