import speech_recognition as sr
from time import perf_counter

r = sr.Recognizer()
r.energy_threshold = 150
r.dynamic_energy_threshold = False
r.pause_threshold = 0.6
r.non_speaking_duration = 0.3
r.operation_timeout = 5

with sr.Microphone(device_index=1) as source:
    print("Stay silent for 1 second while the mic calibrates...")
    r.adjust_for_ambient_noise(source, duration=1)
    r.energy_threshold = max(120, r.energy_threshold)
    print(f"Threshold set to: {r.energy_threshold}")
    print("Speak now.")

    try:
        started = perf_counter()
        audio = r.listen(source, timeout=4, phrase_time_limit=7)
        print(f"Audio captured in {perf_counter() - started:.2f}s. Processing...")
    except sr.WaitTimeoutError:
        print("No speech detected within 4 seconds.")
        raise SystemExit(0)

try:
    started = perf_counter()
    text = r.recognize_google(audio, language="en-US")
    print(f"Recognized in {perf_counter() - started:.2f}s")
    print("You said:", text)
except sr.UnknownValueError:
    print("Could not understand")
except sr.RequestError as e:
    print("Internet error:", e)
except TimeoutError:
    print("Recognition timed out")
