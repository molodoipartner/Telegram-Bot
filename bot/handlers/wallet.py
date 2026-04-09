from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.i18n import t
from bot.handlers.text import send_dashboard, send_welcome
from bot.handlers.start import start
from bot.services.user_service import get_user
from bot.handlers.text import is_user_logged_in
from bot.services.user_service import get_last_message_id, set_last_message_id

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = get_user(user.id)
    was_logged_in = is_user_logged_in(user.id)

    if not was_logged_in:
        await start(update, context)
        return
    
    if (existing_user and not existing_user.get("logged_in_fully")):
        await send_welcome(update, user.id) 
        return
    
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

    # 🔵 Отправляем dashboard
    msg = await send_dashboard(update, user.id)

    # 💾 Сохраняем новый ID
    set_last_message_id(user.id, msg.message_id)