import json
import os

FILE = "data/memory.json"

def load_memory() -> dict:
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_memory(mem: dict):
    os.makedirs(os.path.dirname(FILE), exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(mem, f, indent=4)

def remember(key: str, value: str):
    m = load_memory()
    m[key] = value
    save_memory(m)

def recall(key: str):
    return load_memory().get(key)