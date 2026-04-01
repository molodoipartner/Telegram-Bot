import requests
import os
import json

def fetch_users():
    url = "https://telegram-bot-41j5.onrender.com/users"
    headers = {
        "X-API-KEY": "SECRET123"  # 🔑 тот же ключ
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("✅ Доступ разрешён")

            os.makedirs("newdata", exist_ok=True)
            file_path = os.path.join("newdata", "user.json")

            data = response.json()

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"💾 Файл сохранён: {file_path}")

        elif response.status_code == 403:
            print("🚫 Неверный API ключ")

        else:
            print(f"❌ Ошибка: {response.status_code}")

    except Exception as e:
        print("🚨 Ошибка запроса:", e)


if __name__ == "__main__":
    fetch_users()