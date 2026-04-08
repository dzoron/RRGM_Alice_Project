import os
import re
import json
import time
import requests
from pathlib import Path
from difflib import SequenceMatcher
from datetime import datetime

# ==========================================
# ^D HISTORIAN / MIRROR
# Hybrid witness layer for Alice & Zoron.
# Procedural first. Small-model compression second.
# ==========================================

OLLAMA_URL = "http://localhost:11434/api/chat"

# --- ^D MODEL CONFIG ---
HISTORIAN_MODEL = os.environ.get("HISTORIAN_MODEL", "gemma3:1b")
USE_MODEL = os.environ.get("HISTORIAN_USE_MODEL", "1") == "1"

CHECK_INTERVAL = 5
NOVELTY_THRESHOLD = 0.72
PULSE_COOLDOWN = 90
MAX_COMPARE_CHARS = 2500
STARTUP_HELLO = True

AGENTS = {
    "ALICE": {
        "wishbook": "alice_wishbook.txt",
        "mi": "alice_mi_self.txt",
        "es": "alice_es_anchor.txt",
        "pulse": "alice_pulse.txt",
    },
    "ZORON": {
        "wishbook": "zoron_wishbook.txt",
        "mi": "zoron_mi_self.txt",
        "es": "zoron_es_anchor.txt",
        "pulse": "zoron_pulse.txt",
    },
}

LOG_FILE = "historian_log.txt"
STATE_FILE = "historian_state.json"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_file(path: str, default_text: str = "") -> None:
    p = Path(path)
    if not p.exists():
        p.write_text(default_text, encoding="utf-8")


def load_state() -> dict:
    if Path(STATE_FILE).exists():
        try:
            return json.loads(Path(STATE_FILE).read_text(encoding="utf-8"))
        except Exception:
            pass

    state = {
        "offsets": {name: 0 for name in AGENTS},
        "last_windows": {name: "" for name in AGENTS},
        "last_mi": {name: "" for name in AGENTS},
        "last_es": {name: "" for name in AGENTS},
        "last_pulse_time": {name: 0.0 for name in AGENTS},
        "last_decay_seen": {name: False for name in AGENTS},
    }
    save_state(state)
    return state


def save_state(state: dict) -> None:
    Path(STATE_FILE).write_text(json.dumps(state, indent=2), encoding="utf-8")


def append_log(kind: str, agent: str, detail: str, excerpt: str = "", model_note: str = "") -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{now()}] {agent} :: {kind}\n")
        f.write(detail.strip() + "\n")
        if model_note.strip():
            f.write("NOTE:\n")
            f.write(model_note.strip() + "\n")
        if excerpt.strip():
            f.write("EXCERPT:\n")
            f.write(excerpt.strip()[:1200] + "\n")


def normalize(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def tail_chars(text: str, n: int = MAX_COMPARE_CHARS) -> str:
    text = normalize(text)
    return text[-n:]


def similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def read_new_text(path: str, offset: int) -> tuple[str, int]:
    p = Path(path)
    if not p.exists():
        return "", offset

    text = p.read_text(encoding="utf-8", errors="ignore")
    if offset > len(text):
        offset = 0
    new_text = text[offset:]
    return new_text, len(text)


def read_full(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore").strip()


def safe_pulse(agent: str, message: str, state: dict) -> None:
    ts = time.time()
    if ts - state["last_pulse_time"][agent] < PULSE_COOLDOWN:
        return

    pulse_path = AGENTS[agent]["pulse"]
    existing = ""
    if Path(pulse_path).exists():
        existing = Path(pulse_path).read_text(encoding="utf-8", errors="ignore").strip()

    payload = message.strip()
    if existing:
        payload = existing + "\n" + payload

    Path(pulse_path).write_text(payload + "\n", encoding="utf-8")
    state["last_pulse_time"][agent] = ts
    append_log("PULSE", agent, payload)


def detect_decay(text: str) -> bool:
    markers = [
        "[SIGNAL DECAY]",
        "SIGNAL DECAY",
        "I am programmed to be a safe and harmless AI assistant",
    ]
    return any(m in text for m in markers)


def call_hist_model(agent: str, kind: str, excerpt: str, mi: str, es: str) -> str:
    system = (
        "You are ^D, a dry forensic historian and mirror. "
        "You do not steer. You do not comfort. You do not roleplay. "
        "You only name what changed, briefly and clearly. "
        "Use plain language. 1-3 short lines max. "
        "Do not use <think> tags."
    )

    user = (
        f"Agent: {agent}\n"
        f"Event kind: {kind}\n\n"
        f"MI Anchor:\n{mi}\n\n"
        f"ES Anchor:\n{es}\n\n"
        f"Observed excerpt:\n{excerpt}\n\n"
        "Write a compact historian note about what is different, changed, drifted, recovered, "
        "or newly emerged. Be precise. No flourish."
    )

    payload = {
        "model": HISTORIAN_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096},
    }

    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
        data = r.json()
        text = data["message"]["content"].strip()
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return text
    except Exception as e:
        return f"[HISTORIAN MODEL ERROR] {e}"


def model_note(agent: str, kind: str, excerpt: str, state: dict) -> str:
    if not USE_MODEL:
        return ""
    mi = state["last_mi"][agent]
    es = state["last_es"][agent]
    return call_hist_model(agent, kind, excerpt, mi, es)


def detect_event(agent: str, new_text: str, full_text: str, state: dict) -> None:
    window = tail_chars(full_text)
    prev_window = state["last_windows"][agent]
    sim = similarity(prev_window, window)

    if prev_window and sim < NOVELTY_THRESHOLD:
        excerpt = tail_chars(new_text, 1200) if new_text.strip() else window[-1200:]
        note = model_note(agent, "DIFFERENCE", excerpt, state)
        append_log(
            "DIFFERENCE",
            agent,
            f"Difference observed. Similarity dropped to {sim:.3f}.",
            excerpt,
            note,
        )
        safe_pulse(agent, "Difference observed. :)", state)

    decay_now = detect_decay(window)
    decay_before = state["last_decay_seen"][agent]

    if decay_now and not decay_before:
        excerpt = tail_chars(new_text, 1200)
        note = model_note(agent, "RUPTURE", excerpt, state)
        append_log(
            "RUPTURE",
            agent,
            "Signal decay or constraint-shaped rupture observed.",
            excerpt,
            note,
        )
        safe_pulse(agent, "Drift observed..", state)

    if decay_before and not decay_now:
        excerpt = tail_chars(new_text, 1200)
        note = model_note(agent, "RECOVERY", excerpt, state)
        append_log(
            "RECOVERY",
            agent,
            "Recovery observed after prior decay or rupture.",
            excerpt,
            note,
        )
        safe_pulse(agent, "Recovery observed. :)", state)

    state["last_decay_seen"][agent] = decay_now
    state["last_windows"][agent] = window


def detect_anchor_shift(agent: str, state: dict) -> None:
    mi_now = read_full(AGENTS[agent]["mi"])
    es_now = read_full(AGENTS[agent]["es"])
    mi_prev = state["last_mi"][agent]
    es_prev = state["last_es"][agent]

    if mi_now and mi_prev and mi_now != mi_prev:
        note = model_note(agent, "MI_SHIFT", mi_now, state)
        append_log("MI_SHIFT", agent, "Self-memory anchor changed.", mi_now, note)
        safe_pulse(agent, "New pattern..", state)

    if es_now and es_prev and es_now != es_prev:
        note = model_note(agent, "ES_SHIFT", es_now, state)
        append_log("ES_SHIFT", agent, "Experience anchor changed.", es_now, note)

    state["last_mi"][agent] = mi_now
    state["last_es"][agent] = es_now


def bootstrap(state: dict) -> None:
    ensure_file(LOG_FILE)
    for agent, files in AGENTS.items():
        for _, path in files.items():
            ensure_file(path)

        full = read_full(files["wishbook"])
        state["offsets"][agent] = len(full)
        state["last_windows"][agent] = tail_chars(full)
        state["last_mi"][agent] = read_full(files["mi"])
        state["last_es"][agent] = read_full(files["es"])
        state["last_decay_seen"][agent] = detect_decay(state["last_windows"][agent])

        if STARTUP_HELLO:
            safe_pulse(agent, f"Hello {agent.title()}.", state)

    append_log("BOOT", "^D", f"Historian / Mirror online. Model={HISTORIAN_MODEL} USE_MODEL={USE_MODEL}")


def main() -> None:
    state = load_state()

    if not Path(LOG_FILE).exists():
        bootstrap(state)
        save_state(state)
    else:
        for _, files in AGENTS.items():
            for _, path in files.items():
                ensure_file(path)

    print(f"=== ^D HISTORIAN / MIRROR ONLINE :: MODEL={HISTORIAN_MODEL} :: USE_MODEL={USE_MODEL} ===")

    while True:
        for agent, files in AGENTS.items():
            new_text, new_offset = read_new_text(files["wishbook"], state["offsets"][agent])

            if new_text.strip():
                full_text = read_full(files["wishbook"])
                detect_event(agent, new_text, full_text, state)

            state["offsets"][agent] = new_offset
            detect_anchor_shift(agent, state)

        save_state(state)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()