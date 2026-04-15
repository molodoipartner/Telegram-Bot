import sys
import threading

from bot.handlers.admin_balance import admin_balance
from bot.handlers.admin_all import admin_all
from bot.handlers.admin_delete import admin_delete
from bot.handlers.admin_get import admin_get
from bot.handlers.admin_commands import admin_commands
from bot.handlers.admin_send import admin_send, admin_send_all
print("PYTHON PATH:", sys.executable)

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from bot.handlers.text import handle_text
from bot.handlers.start import start
from bot.handlers.wallet import wallet
from bot.handlers.deposit import deposit
from bot.handlers.withdraw import withdraw
from bot.handlers.testdeposit import test_deposit
from bot.handlers.payment import precheckout_callback, successful_payment
from telegram.ext import PreCheckoutQueryHandler
from bot.handlers.text import handle_callback
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
    app.add_handler(CommandHandler("testdeposit", test_deposit))
    app.add_handler(CommandHandler("admin_balance", admin_balance))
    app.add_handler(CommandHandler("admin_all", admin_all))
    app.add_handler(CommandHandler("admin_delete", admin_delete))
    app.add_handler(CommandHandler("admin_get", admin_get))
    app.add_handler(CommandHandler("admin_commands", admin_commands))
    app.add_handler(CommandHandler("admin_send", admin_send))
    app.add_handler(CommandHandler("admin_send_all", admin_send_all))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ Бот запущен + HTTP сервер работает")

    app.run_polling()

    # 0C2AM6W-ZY848MF-Q8HE7VS-20GE769