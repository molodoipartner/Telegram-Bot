from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers.text import handle_text


from config import TOKEN

from bot.handlers.start import start
from bot.handlers.login import login
from bot.handlers.me import me

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.run_polling()