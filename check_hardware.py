import cv2
import pygame
import time

print("[HARDWARE] Testing Vision...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("[OK] Camera Frame Captured.")
    else:
        print("[WARNING] Camera opened but frame capture failed.")
    cap.release()
else:
    print("[WARNING] Camera 0 could not be opened. Using simulated vision mode.")

print("[HARDWARE] Testing Audio...")
try:
    pygame.mixer.init()
    print("[OK] Pygame Mixer Initialized.")
except Exception as e:
    print(f"[ERROR] Audio Mixer Failure: {e}")

print("HARDWARE_CHECK_COMPLETE")
