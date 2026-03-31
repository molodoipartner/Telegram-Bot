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