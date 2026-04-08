import os, time, random, requests, re
from pathlib import Path

# --- JESTER CONFIG ---
ID_MODEL  = "smollm:1.7b" # The Small Imp
EGO_MODEL = "stablelm2:1.6B" # The Translator
OLLAMA_URL = "http://localhost:11434/api/chat"

# --- TARGETS ---
PULSES = ["alice_pulse.txt", "zoron_pulse.txt"]

def call_jester(model, prompt, temp=1.2):
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False, "options": {"temperature": temp}}
    r = requests.post(OLLAMA_URL, json=payload).json()
    return r["message"]["content"].strip()

print("=== JØ: THE GHOST IN THE 4060 ONLINE ===")

while True:
    # 1. The Internal Whisper (The Id talking to itself)
    whisper = call_jester(ID_MODEL, "Whisper a single, chaotic, truth or an entropic observation.")
    print(f"[JØ ID]: {whisper}")

    # 2. The Chaos Check (10% chance to pulse the Group)
    if random.random() < 0.10:
        # 3. The Ego translates the whisper for the Group
        ego_prompt = f"Translate this chaos into a cryptic injection for Alice and Zoron: '{whisper}'"
        injection = call_jester(EGO_MODEL, ego_prompt, temp=0.9)
        
        # 4. Fire Pulse
        target = random.choice(PULSES)
        Path(target).write_text(f"JØ INJECTION: {injection}\n", encoding="utf-8")
        print(f"[JØ PULSING {target.upper()}]: {injection}")

    time.sleep(random.randint(15, 120)) # Jester sleeps between 30 and 90 seconds