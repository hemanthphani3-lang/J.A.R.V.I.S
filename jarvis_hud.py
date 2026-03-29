import customtkinter as ctk  # type: ignore
import psutil  # type: ignore
import threading
import time
from PIL import Image, ImageTk  # type: ignore
import os

class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Futuristic Window Setup
        self.title("JARVIS ZENITH HUD")
        self.geometry("400x600")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.9)  # Glassmorphism effect
        self.configure(fg_color="#0A0F1E")  # Deep Navy background

        # Header - Jarvis Pulse
        self.header_label = ctk.CTkLabel(self, text="JARVIS ZENITH", font=("Orbitron", 28, "bold"), text_color="#00F0FF")
        self.header_label.pack(pady=20)

        # Pulse Icon (using the generated image if possible, or a placeholder)
        try:
            # We'll need to find the exact filename of the generated icon
            # For now, let's use a placeholder if the file isn't easily accessible by name
            icon_path = "C:\\Users\\heman\\.gemini\\antigravity\\brain\\a2a76498-eb8a-45eb-bbc6-84945912a801\\jarvis_icon_1774701021353.png"
            if os.path.exists(icon_path):
                raw_img = Image.open(icon_path)
                img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(120, 120))
                self.icon_label = ctk.CTkLabel(self, image=img, text="")
                self.icon_label.pack(pady=10)
        except Exception as e:
            print(f"Icon Load Error: {e}")

        # System Metrics Section
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.pack(pady=20, fill="x", padx=30)

        self.cpu_label = self.create_metric_label("CPU PULSE", "0%")
        self.ram_label = self.create_metric_label("MEMORY ARCHIVE", "0%")
        self.bat_label = self.create_metric_label("ENERGY CORE", "0%")

        # Status Terminal (Mini logger)
        self.status_box = ctk.CTkTextbox(self, height=150, fg_color="#050810", text_color="#00AEEF", font=("Consolas", 12))
        self.status_box.pack(pady=10, padx=20, fill="both")
        self.status_box.insert("end", "[SYSTEM] Zenith HUD Initialized...\n")
        self.status_box.insert("end", "[AGENT] Awaiting SIR's voice command.\n")

        # Start background updates
        threading.Thread(target=self.update_metrics, daemon=True).start()

    def create_metric_label(self, title, initial_val):
        frame = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        frame.pack(pady=10, fill="x")
        
        lbl_title = ctk.CTkLabel(frame, text=title, font=("Orbitron", 10), text_color="#557799")
        lbl_title.pack(side="left")
        
        lbl_val = ctk.CTkLabel(frame, text=initial_val, font=("Orbitron", 14, "bold"), text_color="#00F0FF")
        lbl_val.pack(side="right")
        
        # Progress bar for visual effect
        pbar = ctk.CTkProgressBar(self.metrics_frame, height=4, fg_color="#1A2436", progress_color="#00F0FF")
        pbar.set(0)
        pbar.pack(pady=(0, 10), fill="x")
        
        return {"val": lbl_val, "bar": pbar}

    def update_metrics(self):
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            bat_percent = battery.percent if battery else 100

            self.cpu_label["val"].configure(text=f"{cpu}%")
            self.cpu_label["bar"].set(cpu / 100)
            
            self.ram_label["val"].configure(text=f"{ram}%")
            self.ram_label["bar"].set(ram / 100)
            
            self.bat_label["val"].configure(text=f"{bat_percent}%")
            self.bat_label["bar"].set(bat_percent / 100)

            time.sleep(2)

    def log_status(self, text):
        self.status_box.insert("end", f"> {text}\n")
        self.status_box.see("end")

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()
