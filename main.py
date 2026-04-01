import sys
import threading

print("PYTHON PATH:", sys.executable)

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers.text import handle_text
from bot.handlers.start import start
from config import TOKEN

from http_server import run_http  # 👈 добавили

def main():
    # 🔥 запускаем HTTP сервер в отдельном потоке
    threading.Thread(target=run_http, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Бот запущен + HTTP сервер работает")

    app.run_polling()