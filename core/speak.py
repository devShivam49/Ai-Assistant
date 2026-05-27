import pyttsx3
import threading

_lock = threading.Lock()

def speak(text: str, emotion: str = "neutral"):
    if not text:
        return
    print(f"[Jarvis]: {text}")

    rate_map = {"happy": 190, "sad": 142, "stressed": 152,
                "angry": 160, "confused": 158, "neutral": 175}

    def _run():
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            for v in voices:
                if "zira" in v.name.lower() or "female" in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            engine.setProperty("volume", 1.0)
            engine.setProperty("rate", rate_map.get(emotion, 175))
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS] error: {e}")

    with _lock:
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=15)