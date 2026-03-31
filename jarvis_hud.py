import customtkinter as ctk  # type: ignore
import psutil  # type: ignore
import threading
import time
from PIL import Image, ImageTk  # type: ignore
import os
from queue import Empty
import math
import random

class JarvisHUD(ctk.CTk):
    def __init__(self, message_queue=None):
        super().__init__()

        self.message_queue = message_queue
        
        # --- HOLOGRAPHIC OVERLAY SETUP ---
        self.overrideredirect(True) # Remove title bar for true HUD feel
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", "#010101") # Make background transparent
        self.attributes("-alpha", 0.9)
        self.config(bg="#010101") # Matching transparency key
        
        # Center the HUD on screen (Vertical Side bar)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"300x700+{screen_w - 320}+{screen_h // 2 - 350}")

        # Main Layout (Borderless Frame)
        self.main_frame = ctk.CTkFrame(self, fg_color="#010101", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # ICON / ENERGY CORE (Click to Drag)
        try:
            # Look for icon in current directory or specific asset paths
            possible_icons = [
                "jarvis_logo.png"
            ]
            icon_path = None
            for p in possible_icons:
                if os.path.exists(p):
                    icon_path = p
                    break
            
            if icon_path:
                raw_img = Image.open(icon_path)
                self.icon_image = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(100, 100))
                self.icon_label = ctk.CTkLabel(self.main_frame, image=self.icon_image, text="")
                self.icon_label.pack(pady=(40, 10))
                self.icon_label.bind("<B1-Motion>", self.drag_window)
            else:
                raise FileNotFoundError("No icon found")
        except:
            self.icon_label = ctk.CTkLabel(self.main_frame, text="[●]", font=("Orbitron", 40), text_color="#00F0FF")
            self.icon_label.pack(pady=40)

        self.metrics_pane = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.metrics_pane.pack(pady=5, fill="both", expand=True, padx=20)

        # Tech-Ring Canvas (Holographic Interface)
        self.tech_canvas = ctk.CTkCanvas(self.metrics_pane, width=260, height=300, bg="#010101", 
                                       highlightthickness=0, bd=0)
        self.tech_canvas.pack(pady=10)
        
        self.scan_y = 0
        self.scan_dir = 1
        
        # SINGULARITY: ORBITAL WIDGETS (Expanding detail card)
        self.orbital_btn = ctk.CTkButton(self.main_frame, text="EXPAND NEURAL HIVE", font=("Orbitron", 8), 
                                        fg_color="transparent", border_width=1, border_color="#1A2436",
                                        command=self.toggle_orbital)
        self.orbital_btn.pack(pady=5)
        
        self.orbital_pane = ctk.CTkFrame(self.main_frame, fg_color="#050505", height=0)
        self.orbital_pane.pack(fill="x", padx=20) # Packed but zero height
        
        # OMEGA-ORBITS (Final Visual Evolution)
        self.canvas = ctk.CTkCanvas(self.main_frame, width=280, height=150, bg="#010101", 
                                   highlightthickness=0, bd=0)
        self.canvas.pack(pady=10)
        self.angle = 0.0
        self.animate_omega()

        # GHOST DIALOG (Transparent Scroll)
        self.conv_frame = ctk.CTkScrollableFrame(self.main_frame, height=350, fg_color="#010101", 
                                               scrollbar_button_color="#1A2436", scrollbar_button_hover_color="#00F0FF")
        self.conv_frame.pack(pady=20, padx=20, fill="both")

        # Status Pulse
        self.status_lbl = ctk.CTkLabel(self.main_frame, text="AGENT ONLINE", font=("Orbitron", 8), text_color="#557799")
        self.status_lbl.pack(side="bottom", pady=5)

        # NEURAL INPUT CONSOLE (MANUAL OVERRIDE)
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        self.input_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 5))
        
        self.cmd_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Neural Command...", 
                                     font=("Consolas", 10), fg_color="#050505", border_color="#1A2436", 
                                     text_color="#00F0FF", height=30)
        self.cmd_entry.pack(fill="x")
        self.cmd_entry.bind("<Return>", self.submit_neural_command)

        # Start background threads
        threading.Thread(target=self.metrics_pulse, daemon=True).start()
        if self.message_queue:
            threading.Thread(target=self.queue_pulse, daemon=True).start()
        
        self.animate_tech_rings()

    def add_stealth_metric(self, tag, color):
        f = ctk.CTkFrame(self.metrics_pane, fg_color="transparent")
        f.pack(pady=2, fill="x")
        l = ctk.CTkLabel(f, text=tag, font=("Orbitron", 8), text_color="#557799")
        l.pack(side="left")
        v = ctk.CTkLabel(f, text="--%", font=("Orbitron", 10, "bold"), text_color=color)
        v.pack(side="right")
        pb = ctk.CTkProgressBar(self.metrics_pane, height=1, fg_color="#121212", progress_color=color)
        pb.set(0)
        pb.pack(fill="x", pady=(0, 8))
        return {"val": v, "bar": pb}

    def metrics_pulse(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                bat = psutil.sensors_battery()
                
                # Animate Neural Activity (Random pulse to simulate 'thinking' noise)
                neural = random.randint(10, 90)
            except: pass
            time.sleep(3)

    def animate_tech_rings(self):
        """Phase 1: Rotating Metric Rings & Scanning Ray"""
        try:
            self.tech_canvas.delete("tech")
            self.angle += 0.04
            cx, cy = 130, 150
            
            # System Metrics (CPU/RAM/BAT) as animated rings
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            bat = psutil.sensors_battery().percent if psutil.sensors_battery() else 100
            
            # Draw Rings (Cyan/Mood based)
            mood_color = getattr(self, 'current_mood_color', "#00F0FF")
            
            # --- CPU RING (Double Ring) ---
            self.draw_arc_ring(cx, cy, 90, cpu, mood_color, 1.5, "CPU")
            
            # --- RAM RING ---
            self.draw_arc_ring(cx, cy, 70, ram, "#00AEEF", -1.0, "RAM")
            
            # --- BATTERY RING ---
            self.draw_arc_ring(cx, cy, 50, bat, "#00FF7F", 0.5, "PWR")
            
            # --- SCANNING RAY ---
            self.scan_y += 3 * self.scan_dir
            if self.scan_y > 280 or self.scan_y < 20: self.scan_dir *= -1
            self.tech_canvas.create_line(20, self.scan_y, 240, self.scan_y, fill=mood_color, 
                                        width=1, dash=(4,4), tags="tech", stipple="gray50" if os.name != 'nt' else None)
            
            # Numerical labels inside rings
            self.tech_canvas.create_text(cx, cy, text=f"{int(cpu)}%", font=("Orbitron", 14, "bold"), fill=mood_color, tags="tech")
            
            self.after(50, self.animate_tech_rings)
        except: pass

    def draw_arc_ring(self, cx, cy, r, val, color, speed_mult, tag_text):
        a = self.angle * speed_mult
        start_angle = math.degrees(a)
        extent = (val / 100) * 350
        
        # Outer Glowing Path
        self.tech_canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_angle, extent=extent, 
                                   outline=color, width=3, style="arc", tags="tech")
        # Background faint path
        self.tech_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="#121212", width=1, tags="tech")
        
        # Small metric labels
        lx = cx + r * math.cos(a + math.pi/4)
        ly = cy + r * math.sin(a + math.pi/4)
        self.tech_canvas.create_text(lx, ly, text=tag_text, font=("Orbitron", 7), fill="#557799", tags="tech")

    def queue_pulse(self):
        # Mood Color Definitions
        MOOD_COLORS = {
            "CALM": "#00F0FF",      # Cyan
            "EXCITED": "#FFD700",   # Gold
            "SKEPTICAL": "#BD93F9", # Purple
            "ALERT": "#FF5555"      # Red
        }
        
        while True:
            try:
                msg = self.message_queue.get(timeout=1.0)
                if ":" in msg:
                    header, content = msg.split(":", 1)
                    header = header.strip().upper()
                    content = content.strip()
                    
                    if header == "MOOD":
                        new_color = MOOD_COLORS.get(content.upper(), "#00F0FF")
                        self.update_mood_visuals(new_color)
                    else:
                        self.inject_dialog(header, content)
            except Empty: continue
            except: pass

    def update_mood_visuals(self, color):
        """Visual Empathy: Update all HUD accents to match the mood"""
        self.current_mood_color = color
        self.icon_label.configure(text_color=color)
        self.status_lbl.configure(text_color=color)
        self.orbital_btn.configure(border_color=color)

    def inject_dialog(self, sender, text):
        is_jarvis = "JARVIS" in sender.upper()
        color = "#00F0FF" if is_jarvis else "#FFFFFF"
        prefix = ">> " if is_jarvis else "<- "
        
        lbl = ctk.CTkLabel(self.conv_frame, text=f"{prefix}{text}", 
                          font=("Consolas", 11), text_color=color, 
                          wraplength=220, justify="left", anchor="w")
        lbl.pack(pady=4, padx=5, fill="x")
        self.conv_frame._parent_canvas.yview_moveto(1.0)

    def toggle_orbital(self):
        """Singularity Interface: Expand/Collapse Neural Hive"""
        if self.orbital_pane.winfo_height() == 0:
            self.orbital_pane.configure(height=150)
            self.orbital_btn.configure(text="COLLAPSE NEURAL HIVE", text_color="#00F0FF")
            # Populate with dummy 'Hive' data for aesthetic
            for widget in self.orbital_pane.winfo_children(): widget.destroy()
            ctk.CTkLabel(self.orbital_pane, text="[HIVE DISPATCHER ACTIVE]", font=("Orbitron", 8), text_color="#FF00FF").pack(pady=5)
            ctk.CTkLabel(self.orbital_pane, text="> Agent A: Analyzing Data\n> Agent B: Monitoring DNA\n> Agent C: Archiving Memory", 
                        font=("Consolas", 8), text_color="#557799", justify="left").pack(pady=5)
        else:
            self.orbital_pane.configure(height=0)
            self.orbital_btn.configure(text="EXPAND NEURAL HIVE", text_color="#FFFFFF")

    def animate_omega(self):
        """Omega Protocol: Rotating 3D-Style Orbits"""
        try:
            self.canvas.delete("orbit")
            self.angle += 0.05
            cx, cy = 140, 75
            for i in range(3):
                r_w = 60 + i*20
                r_h = 20 + i*10
                a = self.angle * (1 if i%2==0 else -1)
                
                # Draw small circles to form the 'orbit' path
                for dot in range(8):
                    offset = (dot * (math.pi*2 / 8)) + a
                    x1 = cx + r_w * math.cos(offset) * math.cos(0.5) - r_h * math.sin(offset) * math.sin(0.5)
                    y1 = cy + r_w * math.cos(offset) * math.sin(0.5) + r_h * math.sin(offset) * math.cos(0.5)
                    self.canvas.create_oval(x1-2, y1-2, x1+2, y1+2, fill="#00F0FF", outline="", tags="orbit")
            
            self.after(50, self.animate_omega)
        except: pass

    def submit_neural_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        if cmd and self.message_queue:
            # Send to main process with special tag
            self.message_queue.put(f"CMD_INPUT: {cmd}")
            self.cmd_entry.delete(0, 'end')
            self.inject_dialog("USER", cmd)

    def drag_window(self, event):
        x = self.winfo_pointerx() - 150 # Centered on icon
        y = self.winfo_pointery() - 50
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()
