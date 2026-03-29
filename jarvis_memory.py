import json
import os

MEMORY_FILE = "jarvis_memory.json"

def save_memory(fact_type, content):
    try:
        memory = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f: memory = json.load(f)
        
        if fact_type not in memory: memory[fact_type] = []
        memory[fact_type].append({"content": content, "timestamp": os.path.getmtime(MEMORY_FILE) if os.path.exists(MEMORY_FILE) else 0})
        
        with open(MEMORY_FILE, "w") as f: json.dump(memory, f, indent=4)
        return True
    except: return False

def get_memory(fact_type=None):
    try:
        if not os.path.exists(MEMORY_FILE): return {}
        with open(MEMORY_FILE, "r") as f: memory = json.load(f)
        if fact_type: return memory.get(fact_type, [])
        return memory
    except: return {}
