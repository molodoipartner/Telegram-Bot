from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.i18n import t
from bot.handlers.text import send_dashboard
from bot.handlers.start import start
from bot.services.user_service import get_user
from bot.handlers.text import is_user_logged_in

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # ✅ СНАЧАЛА получаем user

    was_logged_in = is_user_logged_in(user.id)

    if not was_logged_in:
        await start(update, context)
    else:
        await send_dashboard(update, user.id)