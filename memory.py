import json
import os
from datetime import datetime

MEMORY_DIR = ".agent_memory"
MEMORY_FILE = "history.json"
MAX_HISTORY = 10


def load_memory(working_dir: str) -> list[dict]:
    memory_path = os.path.join(working_dir, MEMORY_DIR, MEMORY_FILE)
    if not os.path.isfile(memory_path):
        return []
    try:
        with open(memory_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_memory(working_dir: str, prompt: str, result: str, tools_used: list[str]) -> None:
    memory_dir = os.path.join(working_dir, MEMORY_DIR)
    os.makedirs(memory_dir, exist_ok=True)

    history = load_memory(working_dir)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "result": result,
        "tools_used": tools_used,
    })
    history = history[-MAX_HISTORY:]

    memory_path = os.path.join(memory_dir, MEMORY_FILE)
    with open(memory_path, "w") as f:
        json.dump(history, f, indent=2)


def format_memory_for_prompt(history: list[dict]) -> str:
    if not history:
        return ""

    lines = ["Here are previous sessions on this project:"]
    for entry in history:
        lines.append(f"\n- [{entry['timestamp']}] Prompt: \"{entry['prompt']}\"")
        lines.append(f"  Result: {entry['result']}")
        if entry.get("tools_used"):
            lines.append(f"  Tools used: {', '.join(entry['tools_used'])}")

    return "\n".join(lines)
