import json
from bot.services.user_service import get_user

FILE_PATH = "data/translations.json"

def load_translations():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

translations = load_translations()

def t(key, user_id):
    user = get_user(user_id)

    lang = "en"  # язык по умолчанию

    if user and "language" in user:
        lang = user["language"]

    return translations.get(key, {}).get(lang, key)

def get_user_language(user_id):
    user = get_user(user_id)

    if user and "language" in user:
        return user["language"]

    return "en"

def get_image(name, user_id):
    lang = get_user_language(user_id)

    images = {
        "balance": {
            "ru": "images/Human_hand_Ru.jpg",
            "en": "images/Human_hand_En.jpg"
        }
    }

    return images.get(name, {}).get(lang)