import json

FILE_PATH = "data/users.json"

def load_users():
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)