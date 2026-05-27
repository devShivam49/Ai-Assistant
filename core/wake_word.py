import re
import speech_recognition as sr

MIC_INDEX  = 1
WAKE_WORDS = ("jarvis", "jervis", "jarves", "travis")
WAKE_ONLY  = "__wake_only__"

recognizer = sr.Recognizer()
recognizer.energy_threshold         = 100
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold          = 0.6

def init_wake():
    print("[Wake] Calibrating...")
    with sr.Microphone(device_index=MIC_INDEX) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        recognizer.energy_threshold = max(100, recognizer.energy_threshold)
    print(f"[Wake] Ready. Threshold: {recognizer.energy_threshold:.0f}")
    return None, None, None

def _strip_wake(text: str) -> str:
    for word in WAKE_WORDS:
        m = re.search(rf"\b{re.escape(word)}\b", text)
        if m:
            return text[m.end():].strip(" ,.!?")
    return ""

def detect(porcupine, stream) -> str:
    with sr.Microphone(device_index=MIC_INDEX) as source:
        try:
            audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)
            text  = recognizer.recognize_google(audio, language="en-US").lower()
            print(f"[Wake] Heard: {text}")
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            print(f"[Wake] Error: {e}")
            return ""

    if any(w in text for w in WAKE_WORDS):
        cmd = _strip_wake(text)
        return cmd if cmd else WAKE_ONLY
    return ""

def cleanup(porcupine, pa, stream):
    pass