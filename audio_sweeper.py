import speech_recognition as sr
import pyaudio

def sweep_and_lock():
    print("--- JARVIS AUDIO SWEEPER PROTOCOL ---")
    p = pyaudio.PyAudio()
    mics = sr.Microphone.list_microphone_names()
    
    best_index = -1
    max_energy = 0
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"\n[SCANNING INDEX {i}]: {info['name']}")
            try:
                r = sr.Recognizer()
                with sr.Microphone(device_index=i) as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    print(f"  -> Listening for signal... SPEAK NOW!")
                    audio = r.listen(source, timeout=3, phrase_time_limit=2)
                    energy = len(audio.get_raw_data())
                    print(f"  -> ENERGY DETECTED: {energy} units.")
                    if energy > max_energy:
                        max_energy = energy
                        best_index = i
            except Exception as e:
                print(f"  -> [OFFLINE]: {str(e)[:30]}")
    
    if best_index != -1:
        print(f"\n--- SUCCESS: IDEAL SIGNAL FOUND AT INDEX {best_index} ---")
        return best_index
    else:
        print("\n--- CRITICAL: NO AUDIBLE SIGNAL DETECTED ---")
        return -1

if __name__ == "__main__":
    sweep_and_lock()
