from jarvis_system import system_control_logic
import time

def test_system_controls():
    print("Testing System Control Protocol...")
    
    # 1. Volume Test
    print("\n[VOLUME] Testing calibration to 20%...")
    res = system_control_logic("set volume to 20")
    print(f"Result: {res}")
    
    # 2. Window Test (Minimize All)
    print("\n[WINDOW] Testing minimization protocol...")
    res = system_control_logic("minimize all windows")
    print(f"Result: {res}")
    
    # 3. Mute Test
    print("\n[AUDIO] Testing mute protocol...")
    res = system_control_logic("mute system")
    print(f"Result: {res}")
    
    # Restore for usability
    system_control_logic("unmute system")
    system_control_logic("set volume to 50")
    print("\nSystem Restored to safe levels.")

if __name__ == "__main__":
    test_system_controls()
