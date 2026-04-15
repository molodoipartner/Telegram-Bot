from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import html
import re

from bot.utils.file_db import load_users

ADMIN_IDS = [1459737590]


def extract_quoted_parts(text):
    return re.findall(r'"(.*?)"', text, re.DOTALL)

def parse_text(text: str) -> str:
    text = html.escape(text)  # 🔥 защита от HTML
    return re.sub(r"\*(.*?)\*", r"<b>\1</b>", text)



# 🔘 кнопки (поддержка нескольких)
def parse_buttons(buttons_raw):
    keyboard = []

    for btn in buttons_raw:
        if "|" in btn:
            text, url = btn.split("|", 1)

            url = url.strip()

            # фикс ссылки
            if not url.startswith("http"):
                url = "https://" + url

            keyboard.append([InlineKeyboardButton(text.strip(), url=url)])

    return InlineKeyboardMarkup(keyboard) if keyboard else None


# 🔍 поиск пользователя
def find_user(target, users):
    if target.isdigit() and target in users:
        return target

    for uid, data in users.items():
        if data.get("username") == target.replace("@", ""):
            return uid

    return None


# 🚀 ОТПРАВКА ОДНОМУ
async def admin_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет доступа")
        return

    parts = extract_quoted_parts(update.message.text)

    if len(parts) < 1:
        await update.message.reply_text(
            'Использование:\n'
            '/admin_send username "message" "Text|url"'
        )
        return

    raw = update.message.text.split(" ", 2)

    if len(raw) < 2:
        await update.message.reply_text("❌ Укажи username или id")
        return

    target = raw[1]
    users = load_users()

    target_id = find_user(target, users)

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден")
        return

    message = parse_text(parts[0])
    buttons = parse_buttons(parts[1:])

    try:
        await context.bot.send_message(
            chat_id=int(target_id),
            text=message,
            reply_markup=buttons,
            parse_mode="HTML",
            disable_web_page_preview=True
        )

        await update.message.reply_text("✅ Отправлено")

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ошибка отправки")


# 🌍 РАССЫЛКА ВСЕМ
async def admin_send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Нет доступа")
        return

    parts = extract_quoted_parts(update.message.text)

    if not parts:
        await update.message.reply_text(
            'Использование:\n'
            '/admin_send_all "message" "Text|url"'
        )
        return

    message = parse_text(parts[0])
    buttons = parse_buttons(parts[1:])

    users = load_users()

    success, failed = 0, 0

    for uid in users.keys():
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text=message,
                reply_markup=buttons,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            success += 1
        except Exception as e:
            print(f"Ошибка {uid}: {e}")
            failed += 1

    await update.message.reply_text(
        f"📤 Отправлено: {success}\n❌ Ошибки: {failed}"
    )