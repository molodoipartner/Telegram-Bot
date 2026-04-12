from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from bot.utils.file_db import load_users

ADMIN_IDS = [1459737590]


async def admin_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ❌ проверка на админа
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У тебя нет доступа")
        return

    users = load_users()

    # 🔥 берем только залогиненных
    logged_users = [
        (uid, data)
        for uid, data in users.items()
        if data.get("logged_in")
    ]

    if not logged_users:
        await update.message.reply_text("❌ Нет залогиненных пользователей")
        return

    # 🔥 сортировка по времени логина (новые сверху)
    def get_time(u):
        try:
            return datetime.fromisoformat(u[1].get("logged_in_at"))
        except:
            return datetime.min

    logged_users.sort(key=get_time, reverse=True)

    # 🔢 сколько показывать (по умолчанию 20)
    limit = 20
    if context.args:
        try:
            limit = int(context.args[0])
        except:
            pass

    selected_users = logged_users[:limit]

    # 📝 формируем ответ
    text = f"👥 Пользователи (последние {len(selected_users)}):\n\n"

    for uid, data in selected_users:
        username = data.get("username", "no_username")
        balance = data.get("balance", 0)
        pnl = data.get("P&L", 0)

        text += (
            f"👤 @{username}\n"
            f"🆔 {uid}\n"
            f"💰 {balance} | 📈 {pnl}\n\n"
        )

    await update.message.reply_text(text)