import re
import speech_recognition as sr
from core.sounddevice_mic import SoundDeviceMicrophone

WAKE_WORDS = ("jarvis", "jervis", "jarves", "travis")
WAKE_ONLY  = "__wake_only__"

recognizer = sr.Recognizer()
recognizer.energy_threshold         = 100
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold          = 0.4
recognizer.non_speaking_duration    = 0.2

def init_wake():
    # Return the custom microphone and recognizer instances to app.py
    source = SoundDeviceMicrophone()
    rec = sr.Recognizer()
    rec.energy_threshold         = 100
    rec.dynamic_energy_threshold = False
    rec.pause_threshold          = 0.4
    rec.non_speaking_duration    = 0.2
    return source, rec, None

def _strip_wake(text: str) -> str:
    for word in WAKE_WORDS:
        m = re.search(rf"\b{re.escape(word)}\b", text)
        if m:
            return text[m.end():].strip(" ,.!?")
    return ""

def detect(source, rec) -> str:
    r = rec if rec is not None else recognizer
    
    # Save old pause threshold and set wake-specific snappy threshold
    old_pause = r.pause_threshold
    r.pause_threshold = 0.4
    
    try:
        # Wake word is very short. Lower phrase_time_limit to 2.0s for instant recognition.
        audio = r.listen(source, timeout=3, phrase_time_limit=2.0)
        text  = r.recognize_google(audio, language="en-US").lower()
        print(f"[Wake] Heard: {text}")
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except Exception as e:
        print(f"[Wake] Error: {e}")
        return ""
    finally:
        r.pause_threshold = old_pause

    if any(w in text for w in WAKE_WORDS):
        cmd = _strip_wake(text)
        return cmd if cmd else WAKE_ONLY
    return ""

def cleanup(porcupine, pa, stream):
    pass