import speech_recognition as sr

MIC_INDEX = 1

recognizer = sr.Recognizer()
recognizer.energy_threshold         = 100
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold          = 0.8
recognizer.non_speaking_duration    = 0.3

def calibrate(duration: float = 0.8):
    with sr.Microphone(device_index=MIC_INDEX) as source:
        print("[Listen] Calibrating...")
        recognizer.adjust_for_ambient_noise(source, duration=duration)
        recognizer.energy_threshold = max(100, recognizer.energy_threshold)
        print(f"[Listen] Threshold: {recognizer.energy_threshold:.0f}")

def listen() -> str:
    with sr.Microphone(device_index=MIC_INDEX) as source:
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"[Listen] Mic error: {e}")
            return ""
    try:
        text = recognizer.recognize_google(audio, language="en-US").lower()
        print(f"[Listen] Heard: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[Listen] API error: {e}")
        return ""