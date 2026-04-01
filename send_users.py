import requests
import json
import os

def send_users():
    url = "https://telegram-bot-41j5.onrender.com/users"

    headers = {
        "X-API-KEY": "SECRET123"
    }

    file_path = os.path.join("newdata", "user.json")

    try:
        # 📖 читаем файл
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 📡 отправляем
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print("✅ Данные успешно отправлены")
            print(response.json())
        elif response.status_code == 403:
            print("🚫 Неверный API ключ")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(response.text)

    except FileNotFoundError:
        print("❌ Файл не найден:", file_path)
    except Exception as e:
        print("🚨 Ошибка:", e)


if __name__ == "__main__":
    send_users()