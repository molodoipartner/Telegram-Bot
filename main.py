import sys
import threading

print("PYTHON PATH:", sys.executable)

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers.text import handle_text
from bot.handlers.start import start
from bot.handlers.wallet import wallet
from bot.handlers.deposit import deposit
from bot.handlers.withdraw import withdraw

from config import TOKEN

from http_server import run_http  # 👈 добавили

def main():
    # 🔥 запускаем HTTP сервер в отдельном потоке
    threading.Thread(target=run_http, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CommandHandler("wallet", wallet))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))

    print("✅ Бот запущен + HTTP сервер работает")

    app.run_polling()