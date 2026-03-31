from jarvis_web import WebArchitect
import os
import time

def test_architect():
    print("Testing WebArchitect...")
    architect = WebArchitect()
    
    html = "<html><head><title>Test</title></head><body><h1>Hello JARVIS</h1></body></html>"
    css = "body { background: #111; color: #0f0; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }"
    js = "console.log('JARVIS Architect Active');"
    
    project_id = "test_voice_site"
    html_path = architect.create_project(project_id, html, css, js)
    
    if os.path.exists(html_path):
        print(f"Architect Success! Project created at: {html_path}")
        # Verify content
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "style.css" in content and "script.js" in content:
                print("All assets linked correctly.")
            else:
                print("Asset linking FAILED.")
    else:
        print("Architect failed to create project.")

if __name__ == "__main__":
    test_architect()
