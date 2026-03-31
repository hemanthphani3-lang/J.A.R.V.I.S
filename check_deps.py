import importlib
import sys

deps = [
    "requests", "pygame", "edge_tts", "speech_recognition", "cv2", 
    "pyautogui", "psutil", "pycaw", "comtypes", "screen_brightness_control", 
    "dotenv", "telegram", "pygetwindow", "bleak", "zeroconf", "kasa", 
    "easyocr", "duckduckgo_search", "geopy", "bs4", "selenium"
]

missing = []
for d in deps:
    try:
        importlib.import_module(d)
        print(f"[OK] {d}")
    except ImportError:
        missing.append(d)
        print(f"[MISSING] {d}")

if missing:
    print(f"FAILED_DEPS: {','.join(missing)}")
else:
    print("ALL_DEPS_OK")
