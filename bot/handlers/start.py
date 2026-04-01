from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.i18n import t
from bot.services.user_service import get_user

async def send_welcome(update, user_id):
    # кнопка "Продолжить"
    keyboard = [
        [t("continue_button", user_id)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # отправляем картинку + текст
    await update.message.reply_photo(
        photo=open("images/Prew.jpg", "rb"),
        caption=t("welcome_text", user_id),
        parse_mode="HTML",  # ВОТ ЭТО КЛЮЧ 🔥
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    existing_user = get_user(user.id)

    # ✅ если уже залогинен → сразу dashboard
    if existing_user and existing_user.get("logged_in"):
        await send_welcome(update, user.id)
        return

    # ❌ если нет → показываем выбор языка
    keyboard = [
        ["🇬🇧 English", "🇷🇺 Русский"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        t("choose_language", user.id),
        reply_markup=reply_markup
    )