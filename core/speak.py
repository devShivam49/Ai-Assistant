import subprocess
import os
import ctypes
import threading
import pyttsx3

_lock = threading.Lock()

# Premium neural girly voice
NEURAL_VOICE = "en-US-JennyNeural"

def speak(text: str, emotion: str = "neutral"):
    if not text:
        return
    print(f"[Jarvis]: {text}")

    def _speak_neural(text: str) -> bool:
        temp_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp_speech.mp3"))
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass
        
        # Synthesize using edge-tts CLI
        cmd = [
            "python", "-m", "edge_tts",
            "--voice", NEURAL_VOICE,
            "--text", text,
            "--write-media", temp_file
        ]
        
        try:
            # 5-second timeout to fall back quickly if offline or laggy
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        except Exception as e:
            print(f"[TTS] Premium neural synthesis failed, falling back to local TTS: {e}")
            return False
            
        # Play using native Windows MCI
        try:
            ctypes.windll.winmm.mciSendStringW(f'open "{temp_file}" type mpegvideo alias jarvis_speech', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('play jarvis_speech wait', None, 0, 0)
            ctypes.windll.winmm.mciSendStringW('close jarvis_speech', None, 0, 0)
            return True
        except Exception as e:
            print(f"[TTS] Windows MCI playback failed: {e}")
            return False

    def _speak_offline(text: str):
        rate_map = {"happy": 190, "sad": 142, "stressed": 152,
                    "angry": 160, "confused": 158, "neutral": 175}
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
            print(f"[TTS] Offline SAPI5 error: {e}")

    def _run():
        success = _speak_neural(text)
        if not success:
            _speak_offline(text)

    with _lock:
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        t.join(timeout=20)