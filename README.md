# Jarvis Desktop AI Assistant

Jarvis is a Windows desktop AI assistant with voice activation, chat, system automation, memory, and a futuristic PyQt6 interface.

## Current Phase

- PyQt6 desktop shell with transparent neon styling
- Animated assistant orb and voice wave
- System tray support
- Text chat command entry
- Existing wake-word loop preserved
- Existing Ollama brain, memory, and automation actions preserved
- TTS startup made resilient so the app does not crash if Windows SAPI is unavailable

## Run

```powershell
.venv\Scripts\python.exe main.py
```

## Install Dependencies

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Planned Next Steps

1. Replace the temporary speech-recognition wake loop with real Porcupine streaming.
2. Add Faster Whisper command transcription.
3. Add Edge TTS as the primary natural voice engine.
4. Split assistant orchestration into service modules.
5. Add startup registration and a settings dashboard.
6. Add anime sprite or Live2D avatar assets.
