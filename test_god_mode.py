from jarvis_web import WebHost
from jarvis_comm import Communications
import os
import time
import requests

def test_hosting():
    print("Testing WebHosting Protocol...")
    host = WebHost()
    # Create a dummy folder to host
    test_dir = "test_host_dir"
    os.makedirs(test_dir, exist_ok=True)
    with open(os.path.join(test_dir, "index.html"), "w") as f:
        f.write("<h1>JARVIS Host Active</h1>")
    
    url = host.start_hosting(test_dir, port=8080)
    print(f"Host started at: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and "JARVIS" in response.text:
            print("Hosting Success: Content retrieved from localhost.")
        else:
            print("Hosting Failure: Content mismatch.")
    except Exception as e:
        print(f"Hosting Error: {e}")
    finally:
        host.stop_hosting(8080)
        import shutil
        shutil.rmtree(test_dir)

def test_comm():
    print("\nTesting Communications Protocol...")
    comm = Communications()
    # Test WhatsApp link generation (we don't open browser in test)
    res = comm.send_whatsapp("1234567890", "Test Message")
    print(f"WhatsApp logic: {res}")
    
    if "initiated" in res:
        print("Communications Success: Protocol ready.")
    else:
        print("Communications Failure.")

if __name__ == "__main__":
    test_hosting()
    test_comm()
