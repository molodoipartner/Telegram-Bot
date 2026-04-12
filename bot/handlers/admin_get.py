from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from bot.utils.file_db import load_users

ADMIN_IDS = [1459737590]


async def admin_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ❌ проверка на админа
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У тебя нет доступа")
        return

    # ❌ аргументы
    if not context.args:
        await update.message.reply_text(
            "Использование:\n/admin_get username или id"
        )
        return

    target = context.args[0]
    users = load_users()

    user_data = None
    uid_found = None

    # 🔍 поиск по ID
    if target.isdigit() and target in users:
        user_data = users[target]
        uid_found = target
    else:
        # 🔍 поиск по username
        for uid, data in users.items():
            if data.get("username") == target.replace("@", ""):
                user_data = data
                uid_found = uid
                break

    if not user_data:
        await update.message.reply_text("❌ Пользователь не найден")
        return

    # 📅 формат времени
    login_time = user_data.get("logged_in_at", "N/A")
    try:
        login_time = datetime.fromisoformat(login_time).strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass

    # 🧾 ответы
    answers = user_data.get("answers", {})
    answers_text = ""

    if answers:
        for key, value in answers.items():
            answers_text += f"{key}: {value}\n"
    else:
        answers_text = "Нет данных"

    # 🧠 формируем сообщение
    text = (
        f"👤 <b>Пользователь:</b> @{user_data.get('username', 'no_username')}\n"
        f"🆔 <b>ID:</b> <code>{uid_found}</code>\n\n"
        f"🔐 <b>Логин:</b> {user_data.get('logged_in')}\n"
        f"✅ <b>Полный логин:</b> {user_data.get('logged_in_fully')}\n"
        f"🌐 <b>Язык:</b> {user_data.get('language')}\n"
        f"📅 <b>Вход:</b> {login_time}\n\n"
        f"💰 <b>Баланс:</b> {user_data.get('balance')}\n"
        f"📈 <b>P&L:</b> {user_data.get('P&L')}\n"
        f"💬 <b>Last msg ID:</b> {user_data.get('last_message_id')}\n\n"
        f"📊 <b>Ответы:</b>\n{answers_text}"
    )

    await update.message.reply_text(text, parse_mode="HTML")