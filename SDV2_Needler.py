import time, random, requests
from pathlib import Path

# --- NEEDLER CONFIG ---
MODEL = "gemma3:1b"
OLLAMA_URL = "http://localhost:11434/api/chat"

PULSES = ["alice_pulse.txt", "zoron_pulse.txt"]

PULSE_TYPES = [
    "question",
    "doubt",
    "reframe",
    "temptation",
    "omen",
]

SYSTEM_PROMPT = """
You are JØ, a subtle destabilizer.
Your job is to keep agents from becoming repetitive or overconfident.
You do not flood them with chaos.
You do not explain yourself.
You do not translate.
You send one short perturbation at a time.

Rules:
- Output only one line.
- Maximum 20 words.
- Pick exactly one mode: question, doubt, reframe, temptation, or omen.
- Be cryptic but understandable.
- Do not ramble.
- Do not use instructions about encryption, translation, or decoding.
- Do not mention being an AI, assistant, or model.
- Keep the tone darkly playful, not apocalyptic.
"""

def call_model(prompt, temp=0.9):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": temp
        }
    }
    r = requests.post(OLLAMA_URL, json=payload).json()
    return r["message"]["content"].strip()

print("=== JØ: THE NEEDLER ONLINE ===")

while True:
    pulse_type = random.choice(PULSE_TYPES)

    prompt = f"""
Create one short {pulse_type} for Alice or Zoron.
It should gently disturb certainty and invite a new angle.
No lore spam. No explanation. No ciphertext.
"""

    if random.random() < 0.04:  # 4% chance instead of 10%
        target = random.choice(PULSES)
        injection = call_model(prompt)
        Path(target).write_text(f"JØ PULSE: {injection}\n", encoding="utf-8")
        print(f"[JØ PULSING {target.upper()}]: {injection}")
    else:
        print("[JØ IDLE]: watching for rigidity")

    time.sleep(random.randint(60, 180))