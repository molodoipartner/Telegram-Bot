from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.file_db import load_users, save_users

ADMIN_IDS = [1459737590]


async def admin_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ❌ проверка на админа
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У тебя нет доступа")
        return

    # ❌ проверка аргументов
    if not context.args:
        await update.message.reply_text(
            "Использование:\n/admin_delete username или id"
        )
        return

    target = context.args[0]
    users = load_users()

    found = False
    deleted_user = None

    # 🔍 сначала пробуем как ID
    if target.isdigit() and target in users:
        deleted_user = users.pop(target)
        found = True

    else:
        # 🔍 ищем по username
        for uid, data in list(users.items()):
            if data.get("username") == target.replace("@", ""):
                deleted_user = users.pop(uid)
                found = True
                break

    if not found:
        await update.message.reply_text("❌ Пользователь не найден")
        return

    save_users(users)

    username = deleted_user.get("username", "no_username")

    await update.message.reply_text(
        f"🗑 Пользователь @{username} удалён"
    )