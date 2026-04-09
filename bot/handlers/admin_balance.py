import json
from telegram import Update
from telegram.ext import ContextTypes

ADMIN_IDS = [1459737590]  # 🔥 твой Telegram ID
USERS_FILE = "data/users.json"


def load_users():
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


async def admin_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ❌ проверка на админа
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У тебя нет доступа к этой команде")
        return

    # ❌ проверка аргументов
    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование:\n"
            "/admin_balance username amount [pnl]"
        )
        return

    username = context.args[0]

    try:
        amount = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Значение должно быть числом")
        return

    # 🔥 определяем режим (balance или pnl)
    mode = "balance"
    if len(context.args) == 3 and context.args[2].lower() == "pnl":
        mode = "pnl"

    users = load_users()

    # 🔍 ищем пользователя
    found = False
    for uid, data in users.items():
        if data.get("username") == username:
            if mode == "balance":
                data["balance"] = amount
            else:
                data["P&L"] = amount

            found = True
            break

    if not found:
        await update.message.reply_text("❌ Пользователь не найден")
        return

    save_users(users)

    # ✅ ответ
    if mode == "balance":
        await update.message.reply_text(
            f"✅ Баланс @{username} обновлён: {amount}"
        )
    else:
        await update.message.reply_text(
            f"📈 P&L @{username} обновлён: {amount}"
        )