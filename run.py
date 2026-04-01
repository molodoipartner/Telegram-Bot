import os
import threading
from flask import Flask
from main import main

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_bot():
    main()

if __name__ == "__main__":
    # запускаем бота в отдельном потоке
    threading.Thread(target=run_bot).start()

    # запускаем веб-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)