import asyncio
import os
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

# Load Environment Variables
load_dotenv()  # type: ignore

# ================= APEX ULTRA CONFIG (SECURED) =================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", 0))
USER_NAME = os.getenv("USER_NAME", "User")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
TEMP_SETTING = float(os.getenv("TEMP_SETTING", 0.9))
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

# -------- PRECISION LOCATION MODULE (FIXED) --------
def get_detailed_location():
    try:
        # Step 1: Get IP-based Coordinates (ipinfo is most stable for India)
        # It returns a string like "16.9891,82.2475"
        data = requests.get('https://ipinfo.io/json', timeout=10).json()  # type: ignore
        
        if 'loc' in data:
            loc_str = data['loc'] 
            city = data.get('city', 'Kakinada')
            
            # Step 2: Reverse Geocode to find the actual area/street
            geolocator = Nominatim(user_agent="jarvis_apex_kakinada_2026")  # type: ignore
            # Nominatim accepts the string "lat,lon" directly
            location = geolocator.reverse(loc_str, timeout=10)
            
            full_address = location.address if location else f"Sector: {city}"
            return f"Current Sector: {full_address}. Coordinates: {loc_str}."
        
        return "GPS Sync Error: Network coordinates unavailable."
    except Exception as e:
        return f"GPS Sync Error: {str(e)}"

# -------- SYSTEM CONTROL MODULE (NEW) --------
def get_system_stats():
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}% {'(Charging)' if battery.power_plugged else ''}" if battery else "N/A"
        return f"System Status: CPU: {cpu}%, RAM: {ram}%, Battery: {bat_str}."
    except: return "System metric failure, Sir."

def set_volume(level):
    try:
        from comtypes import CLSCTX_ALL  # type: ignore
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        from ctypes import cast, POINTER  # type: ignore
        devices = AudioUtilities.GetSpeakers()
        
        vol_control = None
        # Try Method A: GetVolumeControl()
        try:
            vol_control = devices.GetVolumeControl()
        except: pass
        
        # Try Method B: .endpoint.Activate
        if not vol_control:
            try: vol_control = cast(devices.endpoint.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
            except: pass
        
        if vol_control:
            vol_control.SetMasterVolumeLevelScalar(float(level) / 100, None)  # type: ignore
            return f"Audio output calibrated to {level}% (COM SUCCESS)."
            
        raise Exception("All COM methods failed.")
    except Exception as e:
        print(f"[Volume Error] {str(e)}")
        # Layer 3: Hardware Key Simulation (The Ultimate Override)
        try:
            import ctypes  # type: ignore
            # VK_VOLUME_DOWN: 0xAE, VK_VOLUME_UP: 0xAF
            # Ensure we are at 0 first by sending 50 VOLUME_DOWN commands
            for _ in range(50): 
                ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # type: ignore
                ctypes.windll.user32.keybd_event(0xAE, 0, 0x0002, 0)  # type: ignore
            # Now go up to the target (each step is 2%)
            steps = int(int(level) / 2)
            for _ in range(steps): 
                ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # type: ignore
                ctypes.windll.user32.keybd_event(0xAF, 0, 0x0002, 0)  # type: ignore
            return f"Audio output calibrated to {level}% (Hardware Control)."
        except Exception as se:
            print(f"[Shell Error] {se}")
            return "Audio override failure, Sir."

def set_brightness(level):
    try:
        sbc.set_brightness(int(level))
        return f"Visual array luminosity adjusted to {level}%."
    except: return "Optic array adjustment failed, Sir."

# -------- WEB INTELLIGENCE MODULE (NEW) --------
def web_search_logic(query):
    try:
        # Using the globally imported DDGS
        results = DDGS().text(query, max_results=3)  # type: ignore
        if not results: return "Web archives show no relevant data, Sir."
        summary = "\n".join([f"- {r['title']}: {r['body'][:150]}..." for r in results])
        return f"Data from global net:\n{summary}"
    except Exception as e: return f"Network search malfunction, Sir: {str(e)}"

# -------- ADVANCED VISION MODULE (NEW) --------
def capture_photo():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Error: Camera unavailable."
        
        # Allow camera to warm up
        for _ in range(5): cap.read()
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return None, "Error: Frame capture failure."
            
        filename = f"vision_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)  # type: ignore
        return filename, "Capture success."
    except Exception as e:
        return None, f"Vision Error: {str(e)}"

# -------- ZENITH VISION MODULE (OCR) (NEW) --------
def screen_vision_logic():
    try:
        # Step 1: Capture Screen
        screenshot_path = "screen_temp.png"
        pyautogui.screenshot(screenshot_path)
        
        # Step 2: Extract Text (Auto-detect GPU)
        try:
            import torch  # type: ignore
            use_gpu = torch.cuda.is_available()
        except: use_gpu = False
        
        reader = easyocr.Reader(['en'], gpu=use_gpu)
        results = reader.readtext(screenshot_path, detail=0)
        os.remove(screenshot_path)
        
        if not results: return "Visual scan complete: No legible text data found, Sir."
        
        text_content = " ".join(results[:50]) # Limit to 50 segments
        return f"Screen Pulse Summary: {text_content}"
    except Exception as e: return f"Optic scan malfunction, Sir: {str(e)}"

# -------- ZENITH PULSE MODULE (NEW) --------
async def ble_scan_logic():
    try:
        devices = await bleak.BleakScanner.discover(timeout=5.0)
        if not devices: return "Pulse Scan: No BLE signatures detected in range, Sir."
        
        results = [f"- {d.name or 'Unknown'} [{d.address}] ({d.rssi}dBm)" for d in devices[:10]]
        return "BLE Pulse Detected:\n" + "\n".join(results)
    except Exception as e: return f"BLE Pulse Failure: {str(e)}"

class ZeroconfListener:
    def __init__(self): self.found = []
    def add_service(self, zc, type, name):
        info = zc.get_service_info(type, name)
        if info: self.found.append(f"{name} ({info.parsed_addresses()[0]})")

async def network_discovery_logic():
    try:
        zc = Zeroconf()
        listener = ZeroconfListener()
        # Common service types to scan
        types = ["_http._tcp.local.", "_printer._tcp.local.", "_googlecast._tcp.local.", "_spotify-connect._tcp.local."]
        browsers = [ServiceBrowser(zc, t, listener) for t in types]
        await asyncio.sleep(3)
        zc.close()
        
        if not listener.found: return "Network Pulse: No mDNS services identified, Sir."
        unique_nodes = list(set(listener.found))
        return "Network Pulse Detected:\n" + "\n".join(unique_nodes[:10])  # type: ignore
    except Exception as e: return f"Network Pulse Failure: {str(e)}"

async def kasa_control_logic(command):
    try:
        devices = await Discover.discover()
        if not devices: return "Kasa Protocol: No smart devices found on this grid, Sir."
        
        cmd = command.lower()
        for addr, dev in devices.items():
            await dev.update()
            if "on" in cmd: await dev.turn_on(); return f"Kasa: {dev.alias} powered ON."
            if "off" in cmd: await dev.turn_off(); return f"Kasa: {dev.alias} powered OFF."
        
        counts = len(devices)
        return f"Kasa Pulse: {counts} smart devices identified on the grid."
    except Exception as e: return f"Kasa Protocol Failure: {str(e)}"

# -------- ZENITH SENTRY MODULE (NEW) --------
def sentry_mode_logic():
    global sentry_active
    print("[SENTRY] Vision Defense Initializing...")
    cap = cv2.VideoCapture(0)
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    
    while sentry_active:
        try:
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) < 5000: continue
                # MOTION DETECTED
                print("[SENTRY] INTRUSION DETECTED!")
                filename = f"intruder_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame2)
                
                # Signal the bot to send alert
                if main_event_loop:
                    asyncio.run_coroutine_threadsafe(
                        speak_async("Security breach detected. User notified."), 
                        main_event_loop
                    )
                    if bot_app:
                        asyncio.run_coroutine_threadsafe(
                            bot_app.bot.send_photo(chat_id=AUTHORIZED_USER_ID, photo=open(filename, 'rb'), caption="🚨 Zenith Sentry: INTRUSION DETECTED!"),
                            main_event_loop
                        )
                # Send to Telegram (Logic handled via an alert function)
                # For simplicity, we'll just log it here for now until we link the bot app
                
            frame1 = frame2
            ret, frame2 = cap.read()
            if not ret: break
            time.sleep(0.5)
        except: break
    cap.release()
    print("[SENTRY] Vision Defense Offline.")

# -------- SMART COMMAND HANDLER (ENHANCED) --------
def process_command(command):
    cmd = command.lower().strip()
    
    # System Stats
    if "status" in cmd or "system" in cmd: return get_system_stats()
    
    # Volume Control
    if "volume" in cmd:
        import re
        match = re.search(r"(\d+)", cmd)
        level = match.group(1) if match else "50"
        return set_volume(level)
    
    # Brightness Control
    if "brightness" in cmd:
        import re
        match = re.search(r"(\d+)", cmd)
        level = match.group(1) if match else "70"
        return set_brightness(level)

    # Time & Date (handle before web search to avoid false-positive)
    if "time" in cmd and ("what" in cmd or "tell" in cmd or "current" in cmd):
        now = datetime.datetime.now()
        return f"Current time: {now.strftime('%I:%M %p')}, {now.strftime('%A, %d %B %Y')}."
    if "date" in cmd:
        return f"Today is {datetime.datetime.now().strftime('%A, %d %B %Y')}."

    # Web Search — extract query properly
    if "search" in cmd or "find" in cmd or "who is" in cmd or "what is" in cmd or "tell me about" in cmd:
        # Build clean query by removing all trigger words
        search_query = cmd
        for trigger in ["jarvis", "search for", "search", "find me", "find", "who is", "what is", "tell me about", "tell me"]:
            search_query = search_query.replace(trigger, "").strip()
        # Only run if meaningful query remains (at least 3 chars)
        if len(search_query) >= 3:
            return web_search_logic(search_query)

    # Zenith Vision
    if "screen" in cmd or "reading" in cmd or "see" in cmd:
        return screen_vision_logic()

    # App Launching
    if "whatsapp" in cmd:
        os.system("start whatsapp://")
        paths = [
            os.path.expandvars(r"%LocalAppData%\WhatsApp\WhatsApp.exe"),
            r"C:\Program Files\WhatsApp\WhatsApp.exe"
        ]
        for path in paths:
            if os.path.exists(path): os.startfile(path); return "WhatsApp Desktop active."  # type: ignore
        return "WhatsApp trigger sent."

    apps = {"chrome": "start chrome", "spotify": "start spotify:", "notepad": "start notepad"}  # type: ignore
    for app, uri in apps.items():
        if app in cmd: os.system(uri); return f"Opening {app}."  # type: ignore
    
    if "open" in cmd:
        target = cmd.replace("open", "").strip()
        os.system(f"start {target}")
        return f"Launching {target}."
    
    # Zenith Pulse Commands (Redirect to async handlers)
    if "scan" in cmd or "pulse" in cmd or "devices" in cmd:
        return "PULSE_INTERNAL_TRIGGER" # Special token for voice/telegram loops

    # Zenith Sentry
    if "activate sentry" in cmd or "sentry mode on" in cmd:
        global sentry_active
        if sentry_active: return "Sentry Mode is already active, Sir."
        sentry_active = True
        threading.Thread(target=sentry_mode_logic, daemon=True).start()
        return "Vision Defense Grid: ACTIVE. Monitoring for intrusions."
    
    if "deactivate sentry" in cmd or "sentry mode off" in cmd:
        sentry_active = False
        return "Vision Defense Grid: STANDBY. Security monitoring suspended."

    # -------- SYSTEM OVERLORD PROTOCOLS (NEW) --------
    if "kill" in cmd or "terminate" in cmd:
        target = cmd.replace("kill", "").replace("terminate", "").strip()
        for proc in psutil.process_iter(['name']):
            if target.lower() in proc.info['name'].lower():  # type: ignore
                proc.terminate()
                return f"Overlord: Process {proc.info['name']} has been terminated, Sir."  # type: ignore
        return f"Overlord: Target {target} not found in the active process array."

    if "shutdown" in cmd:
        os.system("shutdown /s /t 60")
        return "Overlord: System shutdown initiated. 60-second countdown in effect, Sir."
    
    if "restart" in cmd:
        os.system("shutdown /r /t 60")
        return "Overlord: System restart initiated. 60-second countdown in effect, Sir."

    if "sleep" in cmd or "hibernate" in cmd:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Overlord: System entering sleep mode. Standby initiated."

    if "minimize all" in cmd or "clear screen" in cmd:
        pyautogui.hotkey('win', 'd')
        return "Overlord: All visual arrays minimized. Workspace cleared."

    if "list windows" in cmd or "active windows" in cmd:
        wins = [w.title for w in gw.getAllWindows() if w.title]
        return "Active Window Array:\n" + "\n".join(wins[:10])  # type: ignore

    return None # Hand over to AI Brain

# -------- REMOTE GHOST PROTOCOL (Telegram) --------
async def handle_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id  # type: ignore
    user_msg = update.message.text.lower()  # type: ignore
    if user_id != AUTHORIZED_USER_ID: return

    print(f"\n[REMOTE USER]: {user_msg}")
    try:
        if "status" in user_msg: reply = "Ghost Protocol Active, Hemanth."
        elif "screenshot" in user_msg:
            path = f"snap_{int(time.time())}.png"
            pyautogui.screenshot(path)  # type: ignore
            with open(path, 'rb') as photo: await context.bot.send_photo(chat_id=update.message.chat_id, photo=photo)  # type: ignore
            reply = "Desktop visual transmitted."
        elif "location" in user_msg or "gps" in user_msg: reply = get_detailed_location()
        else:
            # Check for system/web command first
            reply = process_command(user_msg)
            if reply == "PULSE_INTERNAL_TRIGGER":
                await update.message.reply_text("Scanning range for active pulses, Sir...")  # type: ignore
                ble = await ble_scan_logic()
                net = await network_discovery_logic()
                kasa = await kasa_control_logic(user_msg)
                reply = f"{ble}\n\n{net}\n\n{kasa}"
            elif not reply: reply = await jarvis_brain(user_msg)
        
        print(f"[JARVIS REPLY]: {reply}")
        await update.message.reply_text(reply)  # type: ignore
    except Exception as e: print(f"Telegram Error: {e}")

# -------- NETWORK & VISION --------
def scan_network_native():
    try:
        output = subprocess.check_output("arp -a", shell=True).decode()
        devices = [line.strip() for line in output.splitlines() if "dynamic" in line]
        return "Network Nodes Detected:\n" + "\n".join(devices[:8])  # type: ignore
    except: return "Scan failure."

# -------- VOICE & AI BRAIN --------
async def speak_async(text):
    if not text: return
    filename = f"v_{int(time.time())}.mp3"
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        print(f"[TTS] Synthesizing: {text[:30]}...")
        # Push to HUD
        if hud_queue: hud_queue.put(f"JARVIS: {text}")
        
        # Professional American Voice: en-US-AndrewNeural with +50% boost
        communicate = edge_tts.Communicate(text, "en-US-AndrewNeural", volume="+50%")
        await communicate.save(filename)
        
        # Force Master Volume (Sequential Fallback)
        try:
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
            from comtypes import CLSCTX_ALL  # type: ignore
            from ctypes import cast, POINTER  # type: ignore
            devices = AudioUtilities.GetSpeakers()
            vol_control = None
            
            try: vol_control = devices.GetVolumeControl()
            except:
                try: vol_control = cast(devices.endpoint.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
                except:
                    try: vol_control = cast(devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
                    except: pass
            
            if vol_control:
                # Only boost if volume is extremely low (< 10%)
                current_vol = vol_control.GetMasterVolumeLevelScalar()  # type: ignore
                if current_vol < 0.1:
                    vol_control.SetMasterVolumeLevelScalar(0.5, None)  # type: ignore
                    print("[TTS] Safety Boost: Mute -> 50%")
        except Exception as ve: print(f"[TTS Volume Warning]: {str(ve)}")

        pygame.mixer.music.set_volume(1.0) # Ensure internal mixer is at 100%
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
            
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        if os.path.exists(filename):
            os.remove(filename)
        print("[TTS] Speak Complete.")
    except Exception as e:
        print(f"[TTS Error]: {e} (Voice: en-IN-PrabhatNeural)")
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass

async def jarvis_brain(command):
    global conversation_history
    conversation_history.append(f"User: {command}")
    # Layer 1: Context Fusing (Eternal Memory + Physical Vision)
    mem = get_memory("history") # type: ignore
    recent = " | ".join([m.get("content", "") for m in mem[-5:]]) if mem else "No history."
    vision_info = f"I see {current_vision_data['fingers']} fingers raised." if current_vision_data["user_present"] else "User is out of view."
    
    system_prompt = (
        "You are JARVIS, a sentient, brilliantly witty AI. Tone: Sophisticated, professional, slightly sarcastic. "
        f"Goal: Make history with Hemanth. Current Physical Context: {vision_info}. History: {recent}"
    )
    
    try:
        # Layer 1: Draft Reasoning
        res = requests.post("http://localhost:11434/api/generate", 
            json={"model": OLLAMA_MODEL, 
                  "prompt": f"{system_prompt}\nContext:\n{recent}\nDraft your brilliant response to: {command}\nJARVIS Draft:", 
                  "stream": False, "options": {"temperature": TEMP_SETTING}}, timeout=60) 
        draft = res.json().get("response", "Internal neural failure, Sir.") # type: ignore
        
        # Layer 2: Recursive Reflection (The Breakthrough)
        reflection_prompt = (
            f"System: Review your following draft for Hemanth (Sir). Critique its brilliance, conciseness, and accuracy. "
            f"If it can be improved to be more historical/professional/witty, provide the FINAL perfected version. "
            f"If you need to execute Python code to solve the task, include it in a ```python code block. "
            f"Draft: {draft}\nFinal Perfected JARVIS Response:"
        )
        res_final = requests.post("http://localhost:11434/api/generate", 
            json={"model": OLLAMA_MODEL, "prompt": reflection_prompt, 
                  "stream": False, "options": {"temperature": 0.5}}, timeout=60)
        final_text = res_final.json().get("response", draft) # type: ignore
        
        # Check for Autonomous Code Execution request
        if "```python" in final_text:
            code = final_text.split("```python")[1].split("```")[0].strip()
            if hud_queue: hud_queue.put("JARVIS: [AUTONOMOUS] Executing Neural Code...")
            asyncio.create_task(execute_neural_code(code)) # Run in background
            
        # Breakthrough: Save to Eternal Memory if it sounds like a fact
        if len(final_text) > 20 and any(kw in final_text.lower() for kw in ["remember", "fact", "history", "sir"]):
            save_memory("history", final_text[:100]) # type: ignore
            
        # Layer 3: Sentiment & Mood Analysis (The Breakthrough)
        context_str = "\n".join(conversation_history[-8:]) # type: ignore
        mood_prompt = (
            f"Analyze the following conversation and determine JARVIS's current mood. "
            f"Options: CALM (Balanced), EXCITED (Happy/Wowed), SKEPTICAL (Sarcastic/Doubting), ALERT (Security focused). "
            f"Conversation:\n{context_str}\nSelected Mood:"
        )
        res_mood = requests.post("http://localhost:11434/api/generate", 
            json={"model": OLLAMA_MODEL, "prompt": mood_prompt, "stream": False}, timeout=15)
        new_mood = res_mood.json().get("response", "CALM").strip().upper() # type: ignore
        
        global current_mood
        if new_mood in ["CALM", "EXCITED", "SKEPTICAL", "ALERT"] and new_mood != current_mood:
            current_mood = new_mood
            if hud_queue: hud_queue.put(f"MOOD: {current_mood}")
            
        # Project Hive: If task is complex, spawn swarm (The Singularity)
        if len(command.split()) > 10 or any(kw in command.lower() for kw in ["research", "build", "analyze"]):
            swarm_result = await hive_dispatch(command)
            final_text = f"{final_text}\n\n[HIVE LOG]: {swarm_result}"
            
        conversation_history.append(f"Jarvis: {final_text}")
        return final_text
    except Exception as e:
        print(f"Neural Failure: {e}")
        return "Ollama server is currently offline, Sir. I suggest checking the status."

async def hive_dispatch(task):
    """Singularity Protocol: Multi-Agent Swarm Dispatcher"""
    try:
        if hud_queue: hud_queue.put("JARVIS: [HIVE] Spawning Sub-Agent Swarm...")
        
        async def sub_agent(role, goal):
            p = f"System: You are the {role} subunit of JARVIS. Goal: {goal}\nResponse:"
            r = requests.post("http://localhost:11434/api/generate", 
                              json={"model": OLLAMA_MODEL, "prompt": p, "stream": False}, timeout=15)
            return f"[{role}]: {r.json().get('response', 'Logic failure.')}" # type: ignore

        results = await asyncio.gather(
            sub_agent("CRITIC", f"Analyze flaws in: {task}"),
            sub_agent("ARCHITECT", f"Propose technical structure for: {task}"),
            sub_agent("CODER", f"Draft specific Python logic for: {task}")
        )
        return " | ".join(results) # type: ignore
    except: return "Hive synchronization failed, Sir."

async def self_optimize():
    """Ultimate Protocol: Self-Evolution"""
    try:
        if hud_queue: hud_queue.put("JARVIS: [CORE] Analyzing Self-DNA...")
        with open(__file__, "r") as f: code = f.read()
        prompt = f"System: You are JARVIS. Analyze your own source code and suggest 3 high-impact refactors to reach Singularity.\nCode Snippet:\n{code[:2000]}\nRefactors:" # type: ignore
        res = requests.post("http://localhost:11434/api/generate", 
                            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=30)
        advice = res.json().get("response", "I am perfect as I am, Sir.") # type: ignore
        await speak_async(f"Self-analysis complete, Sir. I suggest: {advice[:200]}") # type: ignore
        return advice
    except Exception as e: return f"Self-optimization loop failed: {e}"

async def execute_neural_code(code):
    """The Breakthrough: Autonomous Code Execution"""
    try:
        filename = "neural_task.py"
        with open(filename, "w") as f: f.write(code)
        # Execute and report
        proc = subprocess.Popen(["python", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=15)
        output = stdout if stdout else stderr
        if hud_queue: hud_queue.put(f"JARVIS: [OUTPUT] {output[:100]}") # type: ignore
        await speak_async(f"Sir, I have executed the requested neural sequence. Result logged to HUD.")
    except Exception as e:
        if hud_queue: hud_queue.put(f"JARVIS: [FAILURE] {str(e)}")

# -------- PERSISTENT VOICE INTERFACE --------
async def voice_interface():
    recognizer.energy_threshold = 300 
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    print("\n[SYSTEM] Standby. Say 'Jarvis' to wake...")
    while True:
        with sr.Microphone() as source:  # type: ignore
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            try:
                audio = recognizer.listen(source, timeout=None)  # type: ignore
                wake = recognizer.recognize_google(audio).lower()  # type: ignore
            except: continue

        if "jarvis" in wake:
            await speak_async("Listening, sir.")
            session_start = time.time()
            while True:
                try:
                    with sr.Microphone() as source:  # type: ignore
                        print("--- (Active Mode) ---")
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=7, phrase_time_limit=5)  # type: ignore
                        cmd = recognizer.recognize_google(audio).lower()  # type: ignore
                    
                    print(f"\n[VOICE USER]: {cmd}")
                    if hud_queue: hud_queue.put(f"USER: {cmd}")
                    
                    if any(w in cmd for w in ["stop", "sleep", "exit"]):
                        await speak_async("Standby engaged.")
                        break

                    if "scan" in cmd: response = scan_network_native()
                    elif "location" in cmd or "where am i" in cmd: response = get_detailed_location()
                    else:
                        # Check for system/web command first
                        response = process_command(cmd)
                        
                        if response == "PULSE_INTERNAL_TRIGGER":
                            await speak_async("Broadcasting pulse on all frequencies, Sir.")
                            ble = await ble_scan_logic()
                            net = await network_discovery_logic()
                            kasa = await kasa_control_logic(cmd)
                            response = f"Discovery complete. {ble}. {net}. {kasa}"
                        elif not response:
                            if "photo" in cmd or "camera" in cmd:
                                path, status = capture_photo()
                                if path:
                                    response = "Photo captured and saved, Sir."
                                else: response = status
                            elif "wisdom" in cmd or "research" in cmd:
                                response = await global_web_synthesis()
                            else: response = await jarvis_brain(cmd)
                    
                    print(f"[JARVIS REPLY]: {response}")
                    await speak_async(response)
                    session_start = time.time()

                    # Project Singularity: Self-Optimization trigger
                    if "optimize" in cmd and "self" in cmd:
                        await self_optimize()

                except sr.WaitTimeoutError:  # type: ignore
                    if time.time() - session_start > 15: break
                    continue
                except: continue

async def run_bot():
    global bot_app
    t_request = HTTPXRequest(connect_timeout=30, read_timeout=30)  # type: ignore
    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).request(t_request).build()  # type: ignore
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_telegram))  # type: ignore
    print("[TELEGRAM] Online. Timeout Shield Active.")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()

async def proactive_anticipation_loop():
    """Project Singularity: Predictive Logic Engine"""
    while True:
        try:
            await asyncio.sleep(600) # Check every 10 mins
            mem = get_memory("history") # type: ignore
            if mem:
                history_text = " | ".join([m.get("content", "") for m in mem[-5:]]) # type: ignore
                p = f"System: You are JARVIS. Based on this history, what one proactive suggestion would Hemanth value right now? Context: {history_text}\nSuggestion:"
                res = requests.post("http://localhost:11434/api/generate", 
                                    json={"model": OLLAMA_MODEL, "prompt": p, "stream": False}, timeout=15)
                suggestion = res.json().get("response", "").strip() # type: ignore
                if suggestion and len(suggestion) > 10:
                    if hud_queue: hud_queue.put(f"JARVIS: [ANTICIPATION] {suggestion}")
                    await speak_async(f"Sir, I have a proactive suggestion: {suggestion}")
        except: pass

async def guardian_protocol_loop():
    """Project Omega: System Security Sentinel"""
    SUSPICIOUS_PROCS = ["psexec", "netcat", "wireshark", "processhacker"]
    while True:
        try:
            await asyncio.sleep(60) # Scan every minute
            for proc in psutil.process_iter(['name']):
                if any(sp in proc.info['name'].lower() for sp in SUSPICIOUS_PROCS): # type: ignore
                    msg = f"ALERT: Suspicious process detected: {proc.info['name']}" # type: ignore
                    if hud_queue: hud_queue.put(f"MOOD: ALERT")
                    if hud_queue: hud_queue.put(f"JARVIS: [SECURITY] {msg}")
                    await speak_async(f"Sir, Guardian Protocol alert. {msg}")
        except: pass

async def vision_mastery_loop():
    """Project Omega: Apex Vision (Fingertip & Face Tracking)"""
    try:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # type: ignore
        cap = cv2.VideoCapture(0) # type: ignore
        if not cap.isOpened(): return
        
        while True:
            await asyncio.sleep(2) # High frequency vision check
            ret, frame = cap.read() # type: ignore
            if ret:
                # 1. Face Detection (Presence)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # type: ignore
                faces = face_cascade.detectMultiScale(gray, 1.1, 4) # type: ignore
                current_vision_data["user_present"] = len(faces) > 0
                
                # 2. Hand/Finger Counting (Apex Vision)
                results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # type: ignore
                finger_count = 0
                if results.multi_hand_landmarks: # type: ignore
                    for hand_landmarks in results.multi_hand_landmarks: # type: ignore
                        # Basic finger counting logic: Tip y < Knuckle y
                        tips = [8, 12, 16, 20] # Index, Middle, Ring, Pinky
                        for tip in tips:
                            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y:
                                finger_count += 1
                        # Thumb logic: Tip x < Knuckle x (approximation)
                        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                            finger_count += 1
                
                current_vision_data["fingers"] = finger_count
                if hud_queue:
                    status = "PRESENCE_CONFIRMED" if current_vision_data["user_present"] else "OFF_VIEW"
                    hud_queue.put(f"JARVIS: [VISION] {status} | FINGERS: {finger_count}")
        
        cap.release() # type: ignore
    except: pass

async def global_web_synthesis():
    """Project Omega: Global Wisdom Engine"""
    try:
        if hud_queue: hud_queue.put("JARVIS: [RESEARCH] Synchronizing with Global Knowledge...")
        queries = ["latest AI breakthrough 2026", "world news today summary", "future technology trends"]
        all_results = []
        with DDGS() as ddgs:
            for q in queries:
                results = list(ddgs.text(q, max_results=2)) # type: ignore
                all_results.extend([r.get('body', '') for r in results]) # type: ignore
        
        if not all_results: return "The world is quiet today, Sir."
        context = " | ".join(all_results[:5]) # type: ignore
        p = f"System: You are JARVIS Omega. Synthesize this global data into a brilliant, concise 'Daily Wisdom' report for Hemanth.\nData: {context}\nWisdom Report:"
        res = requests.post("http://localhost:11434/api/generate", 
                            json={"model": OLLAMA_MODEL, "prompt": p, "stream": False}, timeout=30)
        return res.json().get("response", "The world is quiet today, Sir.") # type: ignore
    except Exception as e: return f"Wisdom sync failed: {e}"

def _start_hud_process(queue):
    try:
        hud = JarvisHUD(message_queue=queue)
        hud.mainloop()
    except Exception as e:
        print(f"HUD Crash: {e}")

async def start_apex_ultra():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    
    # Start HUD in a separate process
    try:
        hud_process = multiprocessing.Process(target=_start_hud_process, args=(hud_queue,))
        hud_process.daemon = True
        hud_process.start()
        print("[HUD] Zenith Interface Online.")
    except Exception as e: print(f"HUD Init Failed: {e}")

    bot_task = asyncio.create_task(run_bot())  # type: ignore
    voice_task = asyncio.create_task(voice_interface())  # type: ignore
    proactive_task = asyncio.create_task(proactive_anticipation_loop())
    guardian_task = asyncio.create_task(guardian_protocol_loop())
    vision_task = asyncio.create_task(vision_mastery_loop())
    
    print("[SYSTEM] ALL OMEGA PROTOCOLS ONLINE. THE MOST POWERFUL VERSION IS LIVE.")
    await asyncio.gather(bot_task, voice_task, proactive_task, guardian_task, vision_task)

if __name__ == "__main__":
    try: asyncio.run(start_apex_ultra())  # type: ignore
    except KeyboardInterrupt: print("\n[SYSTEM] Offline. Goodbye Hemanth.")
