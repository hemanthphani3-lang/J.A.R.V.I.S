import speech_recognition as sr
import time

def probe_microphones():
    print("--- JARVIS AUDIO PROBE PROTOCOL ---")
    mics = sr.Microphone.list_microphone_names()
    print(f"Detected {len(mics)} possible input streams.")
    
    for i, name in enumerate(mics):
        print(f"\n[STREAM {i}]: {name}")
        try:
            r = sr.Recognizer()
            with sr.Microphone(device_index=i) as source:
                print(f"  -> Monitoring signal for 3 seconds... Speak now!")
                # Listen for energy level
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=3, phrase_time_limit=2)
                print(f"  -> SIGNAL DETECTED. Index {i} is responsive.")
        except Exception as e:
            print(f"  -> [OFFLINE]: {str(e)[:50]}")

if __name__ == "__main__":
    probe_microphones()
