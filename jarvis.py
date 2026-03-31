import asyncio
import os
import re
import time
import threading
import subprocess
import datetime
import multiprocessing
import requests  # type: ignore
import pygame  # type: ignore
import edge_tts  # type: ignore
import speech_recognition as sr  # type: ignore
import cv2  # type: ignore
import pyautogui  # type: ignore
import psutil  # type: ignore
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
from comtypes import CLSCTX_ALL  # type: ignore
import screen_brightness_control as sbc  # type: ignore
from dotenv import load_dotenv  # type: ignore
from telegram import Update  # type: ignore
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes  # type: ignore
from telegram.request import HTTPXRequest  # type: ignore
import pygetwindow as gw  # type: ignore
from jarvis_hud import JarvisHUD  # type: ignore
import bleak  # type: ignore
from zeroconf import Zeroconf, ServiceBrowser  # type: ignore
from kasa import Discover  # type: ignore
import easyocr  # type: ignore
from duckduckgo_search import DDGS  # type: ignore
from geopy.geocoders import Nominatim  # type: ignore
from jarvis_memory import save_memory, get_memory
import mediapipe as mp  # type: ignore
from jarvis_web import WebScraper, WebAutomator, WebArchitect, WebHost, web_intelligence_logic
from jarvis_comm import Communications, communication_logic
from jarvis_system import SystemController, system_control_logic

# Load Environment Variables
load_dotenv()  # type: ignore

# ================= APEX ULTRA CONFIG (SECURED) =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))
USER_NAME = os.getenv("USER_NAME", "User")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
TEMP_SETTING = float(os.getenv("TEMP_SETTING", 0.9))
MIC_INDEX = int(os.getenv("MIC_INDEX", 1)) # Default to Headphones or first real mic
# ===============================================================

pygame.mixer.init()  # type: ignore
recognizer = sr.Recognizer()  # type: ignore
conversation_history = []
sentry_active = False # type: ignore
main_event_loop = None # type: ignore
bot_app = None # type: ignore
hud_queue = multiprocessing.Queue() # type: ignore
current_mood = "CALM" # Moods: CALM, EXCITED, SKEPTICAL, ALERT
current_vision_data = {"fingers": 0, "user_present": False}

# -------- PRECISION LOCATION MODULE --------
def get_detailed_location():
    try:
        data = requests.get('https://ipinfo.io/json', timeout=10).json()  # type: ignore
        if 'loc' in data:
            loc_str = data['loc'] 
            city = data.get('city', 'Kakinada')
            geolocator = Nominatim(user_agent="jarvis_apex_2026")  # type: ignore
            location = geolocator.reverse(loc_str, timeout=10)
            full_address = location.address if location else f"Sector: {city}"
            return f"Current Sector: {full_address}. Coordinates: {loc_str}."
        return "GPS Sync Error: Network coordinates unavailable."
    except Exception as e: return f"GPS Sync Error: {str(e)}"

# -------- SYSTEM STATS --------
def get_system_stats():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}% {'(Charging)' if battery.power_plugged else ''}" if battery else "N/A"
        return f"System Status: CPU: {cpu}%, RAM: {ram}%, Battery: {bat_str}."
    except: return "System metric failure, Sir."

# -------- COMMAND ROUTING (THE BRAIN GATEWAY) --------
def process_command(cmd):
    # System Keywords
    if "status" in cmd or "report" in cmd: return get_system_stats()
    
    # Web Logic
    if "search" in cmd or "find" in cmd or "tell me about" in cmd:
        query = cmd.replace("search for", "").replace("search", "").strip()
        if len(query) > 3: return web_intelligence_logic(query)
    
    # -------- WEB INTELLIGENCE PROTOCOLS --------
    if "scrape" in cmd or "extract" in cmd:
        url = re.search(r'(https?://\S+)', cmd)
        if url: return WebScraper().scrape_url(url.group(1))
    
    if "host" in cmd or "hosting" in cmd:
        host = WebHost()
        url = host.start_hosting("web_projects")
        return f"Hosting Protocol Active at {url}."

    # -------- SYSTEM & WORKSPACE CONTROLS --------
    system_keywords = ["volume", "mute", "unmute", "arrange", "workspace", "minimize", "focus", "lock", "sleep"]
    if any(k in cmd for k in system_keywords):
        return system_control_logic(cmd)

    # -------- COMMUNICATION PROTOCOLS --------
    if "text" in cmd or "message" in cmd:
        platform = "whatsapp" if "whatsapp" in cmd else "telegram"
        return f"PULSE_COMM_TRIGGER:{platform}" # Brain handles extraction

    return None # Pass to AI Brain for complex reasoning

# -------- VOICE & AI BRAIN --------
async def speak_async(text):
    if not text: return
    filename = f"v_{int(time.time())}.mp3"
    try:
        print(f"[TTS] Synthesizing: {text[:30]}...")
        if hud_queue: hud_queue.put(f"JARVIS: {text}")
        
        communicate = edge_tts.Communicate(text, "en-US-AndrewNeural", volume="+50%")
        await communicate.save(filename)
        
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): await asyncio.sleep(0.1)
        pygame.mixer.music.stop(); pygame.mixer.music.unload()
        if os.path.exists(filename): os.remove(filename)
    except Exception as e: print(f"[TTS Error]: {e}")

async def jarvis_brain(command):
    global current_mood
    vision_info = f"Tracking: {current_vision_data['fingers']} fingers." if current_vision_data["user_present"] else "Observing environment."
    prompt = f"System: You are JARVIS. Tone: Sophisticated, Sarcastic. Context: {vision_info}\nUser: {command}\nJARVIS:"
    
    try:
        res = requests.post("http://localhost:11434/api/generate", 
                            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=45)
        response = res.json().get("response", "Neural grid unstable, Sir.").strip()
        
        # Mood Tag Extraction
        if "[MOOD: ALERT]" in response: current_mood = "ALERT"
        elif "[MOOD: EXCITED]" in response: current_mood = "EXCITED"
        else: current_mood = "CALM"
        if hud_queue: hud_queue.put(f"MOOD: {current_mood}")
        
        # Handle Autonomous Code execution if brain provides bash/python blocks
        if "```bash" in response:
            code = response.split("```bash")[1].split("```")[0].strip()
            os.system(code) # Fast God Mode triggered
            
        return response
    except: return "Sir, please ensure the Ollama neural core is active."

    # STABILIZED DEFAULT SCAN
    print("\n[SYSTEM] Initializing Master Audio Stream...")
    if hud_queue: hud_queue.put("JARVIS: [SYSTEM] Linking Default Signal...")
    
    # Use default mic (None) with robust energy detection
    try:
        source = sr.Microphone()
        with source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            print("  -> Calibration Complete. System Locked.")
    except Exception as e:
        print(f"  -> Audio Critical Failure: {e}")
        if hud_queue: hud_queue.put("JARVIS: [FATAL] Signal Lost.")
        return

    while True:
        try:
            with source:
                # Listen for wake word
                print("[SYSTEM] Monitoring Pulse...")
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                wake = recognizer.recognize_google(audio).lower()
                print(f"[VOICE]: {wake}")
                
                if "jarvis" in wake:
                    if hud_queue: hud_queue.put("MOOD: EXCITED")
                    await speak_async("Listening, sir.")
                    
                    audio = recognizer.listen(source, timeout=10)
                    cmd = recognizer.recognize_google(audio).lower()
                    print(f"  -> RECEIVED: {cmd}")
                    
                    if hud_queue: hud_queue.put(f"USER: {cmd}")
                    response = process_command(cmd)
                    if not response: response = await jarvis_brain(cmd)
                    await speak_async(response)
                    
        except sr.UnknownValueError: continue
        except Exception as e:
            if hud_queue: hud_queue.put(f"JARVIS: [SYSTEM] Pulse Reset.")
            await asyncio.sleep(1)

# -------- HUB COMMAND HANDLER (MANUAL OVERRIDE) --------
async def handle_hud_commands():
    """Neural Link: Listen for manual text commands from the HUD Console"""
    while True:
        try:
            # Use a non-blocking check to keep loop alive
            if not hud_queue.empty():
                msg = hud_queue.get_nowait()
                if msg.startswith("CMD_INPUT:"):
                    cmd = msg.replace("CMD_INPUT:", "").strip().lower()
                    print(f"\n[MANUAL NEURAL INPUT]: {cmd}")
                    
                    # 1. Routing
                    response = process_command(cmd)
                    if not response: 
                        response = await jarvis_brain(cmd)
                    
                    # 2. Response
                    print(f"[JARVIS REPLY]: {response}")
                    await speak_async(response)
            
            await asyncio.sleep(0.5)
        except Exception as e:
            await asyncio.sleep(1)

# -------- TELEGRAM PROTOCOL --------
async def run_bot():
    try:
        t_request = HTTPXRequest(connect_timeout=30, read_timeout=30)
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(t_request).build()
        await app.initialize(); await app.start(); await app.updater.start_polling()
        print("[TELEGRAM] Neural Link Active.")
    except: print("[TELEGRAM] Failed to sync link.")

# -------- VISION PROTOCOL --------
async def vision_mastery_loop():
    try:
        cap = cv2.VideoCapture(0)
        while True:
            await asyncio.sleep(2)
            ret, frame = cap.read()
            if ret:
                # Update current_vision_data here with real CV logic
                current_vision_data["user_present"] = True
        cap.release()
    except: pass

# -------- STARTUP --------
def _start_hud_process(queue):
    JarvisHUD(message_queue=queue).mainloop()

async def start_apex_ultra():
    # 1. Start HUD Process FIRST to show visual life
    hud_proc = multiprocessing.Process(target=_start_hud_process, args=(hud_queue,))
    hud_proc.daemon = True
    hud_proc.start()
    
    # 2. Start Background Sentinels
    asyncio.create_task(run_bot())
    asyncio.create_task(vision_mastery_loop())
    asyncio.create_task(handle_hud_commands())
    
    # 3. Greet the User
    await speak_async("System online, Sir. Neural grid stabilized.")
    
    # 4. Start Voice Interface (Main Loop)
    await voice_interface()

if __name__ == "__main__":
    try: asyncio.run(start_apex_ultra())
    except KeyboardInterrupt: print("\nOffline. Goodbye Sir.")
