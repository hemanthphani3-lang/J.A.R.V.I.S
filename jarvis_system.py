import os
import ctypes
import pygetwindow as gw # type: ignore
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # type: ignore
from comtypes import CLSCTX_ALL # type: ignore

class SystemController:
    def __init__(self):
        # Audio Setup
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        except: self.volume = None

    def set_volume(self, level):
        """Set master volume (0 to 100)."""
        if not self.volume: return "Audio interface unavailable, Sir."
        try:
            # Level transformation: 0.0 to 1.0
            val = max(0, min(100, int(level))) / 100
            self.volume.SetMasterVolumeLevelScalar(val, None)
            return f"Master volume calibrated to {level} percent, Sir."
        except Exception as e: return f"Volume recalibration failed: {e}"

    def mute_unmute(self, mute=True):
        """Mute/Unmute system audio."""
        if not self.volume: return "Audio interface unavailable, Sir."
        self.volume.SetMute(1 if mute else 0, None)
        return "Audio broadcast suppressed." if mute else "Audio broadcast restored."

    def arrange_workspace(self):
        """Tile all non-minimized windows in a grid layout."""
        try:
            windows = [w for w in gw.getAllWindows() if w.title and not w.isMinimized and w.visible]
            if not windows: return "No active displays identified for tiling, Sir."
            
            import math
            count = len(windows)
            cols = math.ceil(math.sqrt(count))
            rows = math.ceil(count / cols)
            
            screen_w = 1920 # Default fallback, Gw works with relative so this is for calculation
            screen_h = 1080
            
            w = screen_w // cols
            h = screen_h // rows
            
            for i, win in enumerate(windows):
                r, c = i // cols, i % cols
                win.restore()
                win.moveTo(c * w, r * h)
                win.resizeTo(w, h)
                
            return f"Workspace successfully tiled for {count} active targets, Sir."
        except Exception as e: return f"Workspace alignment failed: {e}"

    def focus_app(self, app_name):
        """Bring a specific window to the foreground."""
        try:
            all_wins = gw.getWindowsWithTitle(app_name)
            if all_wins:
                all_wins[0].activate()
                all_wins[0].maximize()
                return f"Initial target focused: {app_name}, Sir."
            return f"Strategic target '{app_name}' not identified in the grid."
        except: return "Unable to focus visual stream, Sir."

    def minimize_all(self):
        """Minimize all windows."""
        try:
            for win in gw.getAllWindows():
                if win.title and win.visible: win.minimize()
            return "All visual streams minimized, Sir."
        except: return "Internal display error, Sir."

    def lock_system(self):
        """Lock the workstation."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Workstation secured. Pulse locked, Sir."
        except: return "Security protocol failed, Sir."

    def sleep_mode(self):
        """Put system to sleep."""
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Entering sleep mode. Standby engaged, Sir."
        except: return "Power management failed, Sir."

# Unified controller function
def system_control_logic(cmd):
    ctrl = SystemController()
    
    if "volume" in cmd:
        import re
        match = re.search(r"(\d+)", cmd)
        if match: return ctrl.set_volume(match.group(1))
        return "Please specify a strategic volume percentage, Sir."
    
    if "mute" in cmd: return ctrl.mute_unmute(mute=True)
    if "unmute" in cmd: return ctrl.mute_unmute(mute=False)
    if "arrange" in cmd or "workspace" in cmd: return ctrl.arrange_workspace()
    if "minimize all" in cmd or "clear visuals" in cmd: return ctrl.minimize_all()
    if "focus" in cmd:
        target = cmd.replace("focus", "").strip()
        return ctrl.focus_app(target)
    if "lock" in cmd: return ctrl.lock_system()
    if "sleep" in cmd: return ctrl.sleep_mode()
    
    return "Neutral system command protocol, Sir."
