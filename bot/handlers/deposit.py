from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.i18n import t
from bot.handlers.text import send_dashboard
from bot.handlers.start import start
from bot.handlers.text import is_user_logged_in

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    was_logged_in = is_user_logged_in(user.id)

    if not was_logged_in:
        await start(update, context)  # ✅ важно: передаём context
    else:
        keyboard = [
            [t("balance_button", user.id)]
        ]

        await update.message.reply_photo(
            photo=open("images/Deposit.jpg", "rb"),
            caption=t("top_up_text", user.id),
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )