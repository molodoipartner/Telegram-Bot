import json

FILE_PATH = "data/users.json"


def load_users():
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)