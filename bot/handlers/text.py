from bot.services.user_service import login_user
from bot.utils.i18n import t
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup
import json
from PIL import Image, ImageDraw, ImageFont
import io
from bot.handlers.start import start
from bot.services.user_service import get_user

def is_user_logged_in(user_id):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(str(user_id))
    if not user:
        return False

    return user.get("logged_in", False)

async def handle_text(update, context):
    user = update.effective_user
    text = update.message.text
    existing_user = get_user(user.id)

    # ✅ разрешённые команды без логина
    allowed = ["🇬🇧 English", "🇷🇺 Русский", "/start"]

    # ❌ если не залогинен → редирект в start()
    if text not in allowed:
        if not (existing_user and existing_user.get("logged_in")):
            await start(update, context)  # 🔥 вот ключевая строка
            return
        
    if text == "🇷🇺 Русский":
        was_logged_in = is_user_logged_in(user.id)  # ← сохраняем ДО логина

        login_user(user.id, user.username, "ru")  # ← обновляем пользователя

        await update.message.reply_text(
            t("language_set", user.id),
            reply_markup=ReplyKeyboardRemove()
        )

        if was_logged_in:
            await send_dashboard(update, user.id)
        else:
            await send_welcome(update, user.id)


    elif text == "🇬🇧 English":
        was_logged_in = is_user_logged_in(user.id)  # ← сохраняем ДО логина

        login_user(user.id, user.username, "en")

        await update.message.reply_text(
            t("language_set", user.id),
            reply_markup=ReplyKeyboardRemove()
        )

        if was_logged_in:
            await send_dashboard(update, user.id)
        else:
            await send_welcome(update, user.id)
    
    elif text in ["Продолжить ➡️", "Continue ➡️", "💼 Мой баланс", "💼 My Balance"]:
        await send_dashboard(update, user.id)

    elif text in ["💳 Deposit", "💳 Пополнить"]:
        keyboard = [
            [t("balance_button", user.id)]
        ]
        await update.message.reply_text(
            t("top_up_text", user.id),
            parse_mode="HTML",
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        
    elif text in ["💸 Вывести", "💸 Withdraw"]:
        keyboard = [
            [t("balance_button", user.id)]
        ]
        await update.message.reply_text(
            t("withdraw_text", user.id),
            parse_mode="HTML",
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    elif text in ["🌐 Сменить язык", "🌐 Change Language"]:
        keyboard = [
            ["🇬🇧 English", "🇷🇺 Русский"]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            t("choose_language", user.id),
            reply_markup=reply_markup
        )



async def send_welcome(update, user_id):
    # кнопка "Продолжить"
    keyboard = [
        [t("continue_button", user_id)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # отправляем картинку + текст
    await update.message.reply_photo(
        photo=open("Prew.jpg", "rb"),
        caption=t("welcome_text", user_id),
        parse_mode="HTML",  # ВОТ ЭТО КЛЮЧ 🔥
        reply_markup=reply_markup
    )

def get_dashboard_keyboard(user_id):
    keyboard = [
        [
            t("dashboard_buttons", user_id)[0],
            t("dashboard_buttons", user_id)[1],
        ],
        [
            t("about_button", user_id)[0],
            t("about_button", user_id)[1],
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)




def get_user_data(user_id):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    return users.get(str(user_id), {
        "balance": 0.0,
        "P&L": 0.0
    })


def generate_balance_image(balance, pnl, user_id):
    width, height = 900, 450
    img = Image.new("RGB", (width, height), color=(3, 12, 30))
    draw = ImageDraw.Draw(img)

    # Шрифты
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_big = ImageFont.truetype("arial.ttf", 70)
        font_small = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 📊 Заголовок (локализация)
    title_text = t("assets_overview", user_id)
    draw.text((60, 50), title_text.replace("<b>", "").replace("</b>", ""), fill=(160, 180, 210), font=font_title)

    # 💰 Баланс
    draw.text((60, 130), f"{balance:,.2f} USD$", fill=(255, 255, 255), font=font_big)

    # 📈 P&L
    pnl_color = (0, 200, 120) if pnl >= 0 else (255, 80, 80)
    pnl_sign = "+" if pnl >= 0 else ""

    initial_balance = balance - pnl

    if initial_balance != 0:
        percent = pnl / initial_balance * 100
    else:
        percent = 0

    pnl_text_template = t("today_pnl", user_id)
    pnl_text_template = pnl_text_template.replace("<b>", "").replace("</b>", "")

    pnl_text = f"{pnl_text_template.split(':')[0]}: {pnl_sign}{pnl:.2f} ({pnl_sign}{percent:.2f}%)"

    draw.text(
        (60, 260),
        pnl_text,
        fill=pnl_color,
        font=font_small
    )

    # 🔹 Линия
    draw.line((60, 320, 840, 320), fill=(50, 70, 100), width=2)

    # 🏦 Нижний текст
    acc_text = t("account_balance", user_id)
    acc_text = acc_text.replace("<b>", "").replace("</b>", "")

    draw.text((60, 350), acc_text, fill=(120, 140, 180), font=font_small)

    # Сохранение
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes

async def send_dashboard(update, user_id):
    user = get_user_data(user_id)

    balance = user.get("balance", 0.0)
    pnl = user.get("P&L", 0.0)

    image = generate_balance_image(balance, pnl, user_id)

    await update.message.reply_photo(
        photo=image,
        caption=t("update_info", user_id),
        parse_mode="HTML",
        reply_markup=get_dashboard_keyboard(user_id)
    )