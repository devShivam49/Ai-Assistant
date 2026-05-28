import json
import re
import ollama
from core.memory import load_memory
from core.emotion import detect_emotion

VALID_ACTIONS = {
    "talk", "search", "open_youtube", "open_google", "open_chrome",
    "open_notepad", "open_vscode", "open_explorer", "time", "summary",
    "shutdown", "restart", "lock", "volume_up", "volume_down",
    "remember", "recall"
}

_history = []

# Quick responses — no Ollama needed
QUICK = {
    "hi": "Hey Shivam! What's up?",
    "hello": "Hello Shivam! How can I help?",
    "hey": "Hey! I'm here.",
    "how are you": "Running perfectly, Shivam! What do you need?",
    "who are you": "I'm Jarvis — your desktop assistant. I can talk, open apps, search, and remember things.",
    "what can you do": "I can chat, open apps, search Google, remember things, tell the time, and control your PC.",
    "thank you": "Anytime, Shivam!",
    "thanks": "Happy to help!",
    "bye": "See you later, Shivam!",
}

QUICK_ACTIONS = [
    (["open youtube", "launch youtube"],           "open_youtube",  "Opening YouTube!"),
    (["open google", "launch google"],             "open_google",   "Opening Google!"),
    (["open chrome", "launch chrome"],             "open_chrome",   "Opening Chrome!"),
    (["open notepad", "launch notepad"],           "open_notepad",  "Opening Notepad!"),
    (["open vscode", "open vs code"],              "open_vscode",   "Opening VS Code!"),
    (["open explorer", "open files"],              "open_explorer", "Opening File Explorer!"),
    (["what time", "current time", "time is it"], "time",          ""),
    (["lock pc", "lock my pc"],                    "lock",          "Locking your PC."),
    (["volume up", "increase volume"],             "volume_up",     "Turning volume up."),
    (["volume down", "decrease volume"],           "volume_down",   "Turning volume down."),
    (["shut down", "shutdown"],                    "shutdown",      "Shutting down your PC."),
    (["restart"],                                  "restart",       "Restarting your PC."),
]

def _clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def _build_prompt(emotion: str, memory: dict) -> str:
    mem_str = json.dumps(memory, indent=2) if memory else "No memory yet."
    return f"""You are Jarvis — a witty, friendly AI assistant for Shivam's Windows PC.

Emotion: {emotion} — adapt your tone accordingly.
Memory: {mem_str}

Reply ONLY with a raw JSON object, no markdown, no extra text.

Format:
{{"action":"<action>","response":"<spoken reply>","data":"<optional>"}}

For remember: add "key" and "value" fields.
For recall: add "key" field.

Actions: talk, search, open_youtube, open_google, open_chrome, open_notepad,
open_vscode, open_explorer, time, summary, shutdown, restart, lock,
volume_up, volume_down, remember, recall

Be natural, witty, concise. Max 2 sentences for talk responses.
"""

def decide(user_input: str) -> dict:
    global _history
    text = user_input.lower().strip()

    # Quick exact match
    if text in QUICK:
        return {"action": "talk", "response": QUICK[text], "data": ""}

    # Quick action match
    for phrases, action, response in QUICK_ACTIONS:
        if any(p in text for p in phrases):
            return {"action": action, "response": response, "data": ""}

    # YouTube search
    m = re.search(r"(?:play|search youtube for|youtube)\s+(.+)", text)
    if m:
        q = m.group(1).strip()
        return {"action": "open_youtube", "response": f"Searching YouTube for {q}!", "data": q}

    # Google search
    m = re.search(r"(?:search(?:\s+for)?|google)\s+(.+)", text)
    if m:
        q = m.group(1).strip()
        return {"action": "search", "response": f"Searching for {q}!", "data": q}

    # Remember pattern
    m = re.search(r"(?:remember|note that?)\s+(.+?)\s+is\s+(.+)", text)
    if m:
        key, val = m.group(1).strip().replace(" ", "_"), m.group(2).strip()
        return {"action": "remember", "key": key, "value": val,
                "response": f"Got it! I'll remember that {key} is {val}.", "data": val}

    # Use Ollama for everything else
    emotion = detect_emotion(user_input)
    memory  = load_memory()

    _history.append({"role": "user", "content": user_input})
    if len(_history) > 20:
        _history = _history[-20:]

    messages = [{"role": "system", "content": _build_prompt(emotion, memory)}] + _history

    try:
        res = ollama.chat(
            model="llama3.2",
            messages=messages,
            options={"temperature": 0.7, "num_predict": 80}
        )
        raw = res["message"]["content"]
        _history.append({"role": "assistant", "content": raw})

        result = json.loads(_clean_json(raw))
        if result.get("action") not in VALID_ACTIONS:
            result["action"] = "talk"
        result.setdefault("data", "")
        return result

    except json.JSONDecodeError:
        return {"action": "talk", "response": raw, "data": ""}
    except Exception as e:
        return {"action": "talk", "response": f"Something went wrong: {e}", "data": ""}

def reset_history():
    global _history
    _history = []