from telegram import Update
from telegram.ext import ContextTypes

ADMIN_IDS = [1459737590]


async def admin_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ❌ проверка на админа
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У тебя нет доступа")
        return

    text = (
        "🛠 <b>Админ команды</b>\n\n"

        "💰 <b>/admin_balance</b>\n"
        "Обновить баланс или P&L пользователя\n"
        "Использование:\n"
        "<code>/admin_balance username amount</code>\n"
        "<code>/admin_balance username amount pnl</code>\n\n"

        "👥 <b>/admin_all</b>\n"
        "Показать список пользователей\n"
        "Использование:\n"
        "<code>/admin_all</code> — последние 20\n"
        "<code>/admin_all 50</code> — последние 50\n\n"

        "🔍 <b>/admin_get</b>\n"
        "Показать всю информацию о пользователе\n"
        "Использование:\n"
        "<code>/admin_get username</code>\n"
        "<code>/admin_get id</code>\n\n"

        "🗑 <b>/admin_delete</b>\n"
        "Удалить пользователя\n"
        "Использование:\n"
        "<code>/admin_delete username</code>\n"
        "<code>/admin_delete id</code>\n\n"

        "📢 <b>Скоро можно добавить:</b>\n"
        "• бан пользователя\n"
        "• рассылка\n"
        "• статистика\n"
    )

    await update.message.reply_text(text, parse_mode="HTML")