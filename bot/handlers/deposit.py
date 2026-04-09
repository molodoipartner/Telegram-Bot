from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.i18n import t
from bot.handlers.start import send_welcome, start
from bot.handlers.text import is_user_logged_in
from bot.services.user_service import get_last_message_id, get_user, set_last_message_id

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = get_user(user.id)
    was_logged_in = is_user_logged_in(user.id)

    if not was_logged_in:
        await start(update, context)
        return

    if (existing_user and not existing_user.get("logged_in_fully")):
        await send_welcome(update, user.id) 
        return
    
    keyboard = [
        [t("balance_button", user.id)]
    ]

    caption = t("top_up_text", user.id)

    last_message_id = get_last_message_id(user.id)

    # 🟢 Удаляем старое сообщение
    if last_message_id:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=last_message_id
            )
        except Exception as e:
            print("Ошибка удаления:", e)

    # 🔵 Отправляем новое
    msg = await update.message.reply_photo(
        photo=open("images/Deposit.jpg", "rb"),
        caption=caption,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

    # 💾 Сохраняем новый message_id
    set_last_message_id(user.id, msg.message_id)