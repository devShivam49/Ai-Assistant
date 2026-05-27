import speech_recognition as sr
import time

r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.pause_threshold = 1.0

# Test different thresholds
for threshold in [50, 100, 150, 200, 300]:
    r.energy_threshold = threshold
    print(f"\nTesting threshold: {threshold}")
    print("Say 'hello jarvis' now!")
    
    with sr.Microphone(device_index=1) as source:
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=5)
            text = r.recognize_google(audio, language="en-US")
            print(f"✅ threshold {threshold} worked! Heard: {text}")
            break
        except sr.UnknownValueError:
            print(f"❌ threshold {threshold} - could not understand")
        except sr.WaitTimeoutError:
            print(f"⏱ threshold {threshold} - timeout")
        except Exception as e:
            print(f"Error: {e}")
    
    time.sleep(1)