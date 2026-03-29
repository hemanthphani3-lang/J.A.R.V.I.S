import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3")

try:
    res = requests.get("http://localhost:11434/api/tags", timeout=10)
    if res.status_code == 200:
        models = [m['name'] for m in res.json().get('models', [])]
        if any(MODEL in m for m in models):
            print(f"OLLAMA_OK: Model {MODEL} found.")
        else:
            print(f"OLLAMA_WARNING: Model {MODEL} not found in available tags: {models}")
    else:
        print(f"OLLAMA_ERROR: Status code {res.status_code}")
except Exception as e:
    print(f"OLLAMA_ERROR: {e}")
