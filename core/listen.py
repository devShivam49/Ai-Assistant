import speech_recognition as sr
from core.sounddevice_mic import SoundDeviceMicrophone

recognizer = sr.Recognizer()
recognizer.energy_threshold         = 100
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold          = 0.6  # Optimized for snappier command detection
recognizer.non_speaking_duration    = 0.3

def calibrate(source=None, rec=None, duration: float = 0.8):
    r = rec if rec is not None else recognizer
    if source is not None:
        print("[Listen] Calibrating on shared stream...")
        r.adjust_for_ambient_noise(source, duration=duration)
        r.energy_threshold = max(100, r.energy_threshold)
        print(f"[Listen] Threshold: {r.energy_threshold:.0f}")
    else:
        with SoundDeviceMicrophone() as src:
            print("[Listen] Calibrating...")
            r.adjust_for_ambient_noise(src, duration=duration)
            r.energy_threshold = max(100, r.energy_threshold)
            print(f"[Listen] Threshold: {r.energy_threshold:.0f}")

def listen(source=None, rec=None) -> str:
    r = rec if rec is not None else recognizer
    
    # Temporarily set pause_threshold for snappier command listening
    old_pause = r.pause_threshold
    r.pause_threshold = 0.6
    
    try:
        if source is not None:
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
        else:
            with SoundDeviceMicrophone() as src:
                audio = r.listen(src, timeout=6, phrase_time_limit=8)
    except sr.WaitTimeoutError:
        return ""
    except Exception as e:
        print(f"[Listen] Mic error: {e}")
        return ""
    finally:
        r.pause_threshold = old_pause

    try:
        text = r.recognize_google(audio, language="en-US").lower()
        print(f"[Listen] Heard: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[Listen] API error: {e}")
        return ""