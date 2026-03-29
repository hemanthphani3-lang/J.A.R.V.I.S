from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

with open("audio_diag_v3.txt", "w") as f:
    try:
        devices = AudioUtilities.GetSpeakers()
        f.write(f"Device Wrapper: {type(devices)}\n")
        
        if hasattr(devices, 'GetVolumeControl'):
            f.write("Testing GetVolumeControl()...\n")
            vol = devices.GetVolumeControl()
            f.write(f"  - [SUCCESS] Type: {type(vol)}\n")
            if hasattr(vol, 'GetMasterVolumeLevelScalar'):
                f.write(f"  - [VOL] {vol.GetMasterVolumeLevelScalar()}\n")
            else:
                # Need to cast?
                vol_control = cast(vol, POINTER(IAudioEndpointVolume))
                f.write(f"  - [VOL (Casted)] {vol_control.GetMasterVolumeLevelScalar()}\n")

    except Exception as e:
        f.write(f"Fatal: {e}\n")
