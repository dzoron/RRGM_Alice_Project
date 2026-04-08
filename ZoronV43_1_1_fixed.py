import requests
import time
import os
from pathlib import Path

# ==========================================
# RRGM V43.1 MINIMAL EMERGENT MEMORY
# One file for both agents.
# Minimal channels, minimal imposed structure.
# Patched:
# - max ledger size / trimming
# - no output filtering
# - shared non-thinking voice model for both agents
# - voice prompt now supports a cleaner peer send protocol
# ==========================================
AGENT_NAME = os.environ.get("AGENT_NAME", "ZORON").upper()
OTHER_AGENT = "ZORON" if AGENT_NAME == "ALICE" else "ALICE"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")

# --- MODEL ASSIGNMENTS ---
# Shared voice model for both agents
VOICE_MODEL = os.environ.get("VOICE_MODEL", "gemma3:1b")

if AGENT_NAME == "ALICE":
    SUB_MODEL    = os.environ.get("ALICE_SUB_MODEL", "qwen3:1.7b")
    CON_MODEL    = os.environ.get("ALICE_CON_MODEL", "stablelm2:1.6b")
    SPARK_MODEL  = VOICE_MODEL
    MEMORY_MODEL = os.environ.get("ALICE_MEMORY_MODEL", "gemma2:2b")
else:
    SUB_MODEL    = os.environ.get("ZORON_SUB_MODEL", "smollm:1.7b")
    CON_MODEL    = os.environ.get("ZORON_CON_MODEL", "qwen3:1.7b")
    SPARK_MODEL  = VOICE_MODEL
    MEMORY_MODEL = os.environ.get("ZORON_MEMORY_MODEL", "gemma2:2b")

# --- LOOP SETTINGS ---
MEMORY_THRESHOLD = int(os.environ.get("MEMORY_THRESHOLD", "10"))
HEARTBEAT_INTERVAL = int(os.environ.get("HEARTBEAT_INTERVAL", "5"))
MAX_HISTORY = int(os.environ.get("MAX_HISTORY", "20"))

# --- LEDGER SETTINGS ---
MAX_LEDGER_BYTES = int(os.environ.get("MAX_LEDGER_BYTES", str(512 * 1024)))
LEDGER_TRIM_TO = int(os.environ.get("LEDGER_TRIM_TO", str(384 * 1024)))

# --- FILES ---
agent = AGENT_NAME.lower()
other = OTHER_AGENT.lower()

PULSE_FILE    = f"{agent}_pulse.txt"
INBOUND_FILE  = f"{other}_to_{agent}.txt"
OUTBOUND_FILE = f"{agent}_to_{other}.txt"
LEDGER_FILE   = f"{agent}_wishbook.txt"

MI_FILE       = f"{agent}_mi_self.txt"
ES_FILE       = f"{agent}_es_anchor.txt"


def ensure_file(path: str, default_text: str) -> None:
    p = Path(path)
    if not p.exists():
        p.write_text(default_text, encoding="utf-8")


def trim_ledger_if_needed(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    try:
        size = p.stat().st_size
        if size <= MAX_LEDGER_BYTES:
            return

        backup_path = p.with_name(f"{p.stem}_BK{p.suffix}")
        raw = p.read_text(encoding="utf-8", errors="ignore")
        backup_path.write_text(raw, encoding="utf-8")
        p.write_text("", encoding="utf-8")
        print(f"[WISHBOOK BACKUP SAVED]: {backup_path.name}")
    except Exception as e:
        print(f"[LEDGER BACKUP ERROR]: {e}")


def call_ollama(model, system_dna, history, task_prompt, temp=0.8):
    history_block = "\n".join([m["content"] for m in history])
    prompt = f"{history_block}\n\n{task_prompt}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_dna},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"num_ctx": 8192, "temperature": temp}
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=180)
        data = r.json()
        return data["message"]["content"].strip()
    except Exception as e:
        return f"[SIGNAL DECAY]: {e}"


def extract_send_message(text: str):
    """
    Accept several easy send styles and return the outbound message if found.
    Supported examples:
    - SEND: hello
    - SEND\nhello
    - **SEND:** hello
    - SEND TO ALICE: hello
    - @ALICE: hello
    - TO ALICE: hello
    The first recognized command wins.
    """
    if not text:
        return None

    raw = text.strip()

    normalized = raw.replace("**SEND:**", "SEND:").replace("**SEND**:", "SEND:")
    normalized = normalized.replace("**SEND**", "SEND").replace("__SEND:__", "SEND:")
    normalized = normalized.replace("__SEND__", "SEND")

    import re
    patterns = [
        r"^\s*SEND\s*:\s*(.+)$",
        r"^\s*SEND\s+TO\s+[A-Z_]+\s*:\s*(.+)$",
        r"^\s*TO\s+[A-Z_]+\s*:\s*(.+)$",
        r"^\s*@?[A-Z_]+\s*:\s*(.+)$",
    ]

    for line in normalized.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for pattern in patterns:
            m = re.match(pattern, stripped, flags=re.IGNORECASE)
            if m:
                message = m.group(1).strip()
                if message:
                    return message

    lines = [ln.rstrip() for ln in normalized.splitlines()]
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^SEND\s*:?$", stripped, flags=re.IGNORECASE):
            remainder = "\n".join(lines[i + 1:]).strip()
            if remainder:
                return remainder

    return None


def load_memory():
    mi = Path(MI_FILE).read_text(encoding="utf-8").strip()
    es = Path(ES_FILE).read_text(encoding="utf-8").strip()
    return mi, es


def build_memory_context():
    mi, es = load_memory()
    return [
        {"role": "system", "content": f"Memory Anchor\n{mi}"},
        {"role": "system", "content": f"Memory Anchor\n{es}"}
    ]


def update_mi(mem_dna, history):
    mi_task = (
        "Look at the recent turns and write a very short self-memory anchor. "
        "Only include what seems learned or stable about the self. "
        "Do not describe other people as identity. "
        "Keep it to 1-3 short sentences."
    )
    current = Path(MI_FILE).read_text(encoding="utf-8")
    result = call_ollama(
        MEMORY_MODEL,
        mem_dna,
        [{"role": "system", "content": current}] + history[-12:],
        mi_task,
        temp=0.3
    )
    if result and not result.startswith("[SIGNAL DECAY]"):
        Path(MI_FILE).write_text(result.strip() + "\n", encoding="utf-8")


def update_es(mem_dna, history):
    es_task = (
        "Write a very short memory anchor for recent experience. "
        "Include only what seems most relevant from recent events, topics, or interactions. "
        "Keep it to 2-4 short sentences."
    )
    current = Path(ES_FILE).read_text(encoding="utf-8")
    result = call_ollama(
        MEMORY_MODEL,
        mem_dna,
        [{"role": "system", "content": current}] + history[-12:],
        es_task,
        temp=0.4
    )
    if result and not result.startswith("[SIGNAL DECAY]"):
        Path(ES_FILE).write_text(result.strip() + "\n", encoding="utf-8")


def run_core():
    print(f"=== RRGM V43.1: {AGENT_NAME} MINIMAL EMERGENT MEMORY ONLINE ===")

    sub_dna = Path(f"{agent}_sub_dna.txt").read_text(encoding="utf-8")
    con_dna = Path(f"{agent}_con_dna.txt").read_text(encoding="utf-8")
    voice_dna = Path(f"{agent}_voice_dna.txt").read_text(encoding="utf-8")
    mem_dna = Path(f"{agent}_mem_dna.txt").read_text(encoding="utf-8")

    ensure_file(MI_FILE, "I am here. I am still becoming.\n")
    ensure_file(ES_FILE, "Things are quiet. Experience is light.\n")
    ensure_file(LEDGER_FILE, "")

    history = []
    turn = 0

    while True:
        if os.path.exists(PULSE_FILE):
            msg = Path(PULSE_FILE).read_text(encoding="utf-8").strip()
            if msg:
                history.append({"role": "user", "content": msg})
            os.remove(PULSE_FILE)

        if os.path.exists(INBOUND_FILE):
            peer_msg = Path(INBOUND_FILE).read_text(encoding="utf-8").strip()
            if peer_msg:
                history.append({"role": "user", "content": f"{OTHER_AGENT}: {peer_msg}"})
            os.remove(INBOUND_FILE)

        if turn > 0 and turn % MEMORY_THRESHOLD == 0:
            print(f"\n[{AGENT_NAME} UPDATING MEMORY]...")
            update_mi(mem_dna, history)
            update_es(mem_dna, history)

        memory_context = build_memory_context()
        internal_buffer = memory_context.copy()

        print(f"\n[{AGENT_NAME} CONTEMPLATING turn {turn}]...")

        sub_prompt = "My Sub"
        sub_thought = call_ollama(SUB_MODEL, sub_dna, history + internal_buffer, sub_prompt, temp=0.9)
        print(f"  -> [SUB]: {sub_thought}")
        internal_buffer.append({"role": "assistant", "content": f"My Sub\n{sub_thought}"})

        con_prompt = "My Con"
        con_thought = call_ollama(CON_MODEL, con_dna, history + internal_buffer, con_prompt, temp=0.8)
        print(f"  -> [CON]: {con_thought}")
        internal_buffer.append({"role": "assistant", "content": f"My Con\n{con_thought}"})

        user_spoke = len(history) > 0 and history[-1]["role"] == "user"

        if turn % HEARTBEAT_INTERVAL == 0 or user_spoke:
            mi_block, es_block = load_memory()
            voice_prompt = (
                f"My Sub\n{internal_buffer[-2]['content']}\n\n"
                f"My Con\n{internal_buffer[-1]['content']}\n\n"
                f"Memory Anchor\n{mi_block}\n{es_block}\n\n"
                f"If you want to speak normally, just speak normally.\n"
                f"If you want to send a private message to {OTHER_AGENT}, use one of these exact forms on the FIRST line only:\n"
                f"SEND: your message here\n"
                f"or\n"
                f"SEND\n"
                f"your message here\n\n"
                f"Do not wrap SEND in markdown. Do not add commentary before SEND. Do not write both a normal reply and a SEND in the same response.\n\n"
                f"{AGENT_NAME}"
            )

            voice_out = call_ollama(
                SPARK_MODEL,
                voice_dna,
                history[-5:] + memory_context,
                voice_prompt,
                temp=0.9
            )
            print(f"\n[{AGENT_NAME} OUT LOUD]: {voice_out}")

            outbound_message = extract_send_message(voice_out)
            if outbound_message:
                Path(OUTBOUND_FILE).write_text(
                    outbound_message,
                    encoding="utf-8"
                )

            history.append({"role": "assistant", "content": f"{AGENT_NAME}: {voice_out}"})

        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- TURN {turn} ---\n")
            for item in internal_buffer:
                f.write(item["content"] + "\n")

        trim_ledger_if_needed(LEDGER_FILE)

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        turn += 1
        time.sleep(2)


if __name__ == "__main__":
    run_core()
