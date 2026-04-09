from datetime import datetime

from bot.utils.file_db import load_users, save_users

def save_user(user_id, username):
    data = load_users()

    data[str(user_id)] = {
        "username": username,
        "logged_in": True
    }

    save_users(data)

def get_user(user_id):
    data = load_users()
    return data.get(str(user_id))

def set_language(user_id, language):
    data = load_users()

    user = data.get(str(user_id), {})

    user["language"] = language

    data[str(user_id)] = user

    save_users(data)

def login_user(user_id, username, language):
    data = load_users()

    data[str(user_id)] = {
        "username": username,
        "logged_in": True,
        "logged_in_fully": False,
        "logged_in_at": datetime.now().isoformat(),
        "language": language,
        "balance": 0.00,
        "P&L": 0.00
    }

    save_users(data)

def set_last_message_id(user_id, message_id):
    data = load_users()
    user = data.get(str(user_id), {})

    user["last_message_id"] = message_id

    data[str(user_id)] = user
    save_users(data)


def get_last_message_id(user_id):
    data = load_users()
    user = data.get(str(user_id), {})

    return user.get("last_message_id")