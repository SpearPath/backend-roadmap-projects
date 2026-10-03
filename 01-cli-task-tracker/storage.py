import json
from pathlib import Path

FILE_PATH = Path("tasks.json")

def save_tasks(tasks: list) -> None:
    with open(FILE_PATH, "w") as file:
        json.dump(tasks, file,indent= 4)

def load_tasks() -> list:
    if not FILE_PATH.exists():
        return []

    # If the file exists but is 0 bytes, treat it as empty
    if FILE_PATH.stat().st_size == 0:
        return []

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Gracefully handle corrupted or malformed content
        return []