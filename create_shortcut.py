import os
import subprocess

def create_jarvis_shortcut():
    """Create a professional Desktop Shortcut for JARVIS using a VBS helper."""
    # Automatically resolve the system Desktop path (OneDrive aware)
    import subprocess
    desktop = subprocess.check_output(["powershell", "-command", "[Environment]::GetFolderPath('Desktop')"], text=True).strip()
    shortcut_path = os.path.join(desktop, "JARVIS.lnk")
    target_path = os.path.join(os.getcwd(), "launcher.bat")
    icon_path = os.path.join(os.getcwd(), "jarvis_logo.ico") # Use local ICO for Windows Shell
    
    if not os.path.exists(icon_path):
        # Fallback to a placeholder icon if the primary is missing
        icon_path = ""

    # VBScript to create the shortcut
    vbs_content = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{target_path}"
    oLink.WorkingDirectory = "{os.getcwd()}"
    oLink.IconLocation = "{icon_path}, 0"
    oLink.Description = "Summon JARVIS"
    oLink.Save
    """
    
    vbs_file = "create_shortcut.vbs"
    with open(vbs_file, "w") as f:
        f.write(vbs_content)
        
    try:
        subprocess.run(["cscript", "//nologo", vbs_file], check=True)
        print(f"JARVIS Shortcut created successfully on your Desktop!")
    except Exception as e:
        print(f"Failed to create shortcut: {e}")
    finally:
        if os.path.exists(vbs_file):
            os.remove(vbs_file)

if __name__ == "__main__":
    create_jarvis_shortcut()
