import asyncio

from bot.services.user_service import get_last_message_id, login_user, get_user, set_language, set_last_message_id
from bot.utils.file_db import load_users, save_users
from bot.utils.i18n import t, get_image
from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton



import json
from PIL import Image, ImageDraw, ImageFont
import io
from bot.handlers.start import start
import os

def set_user_language(user_id, language):
    data = load_users()

    user_id = str(user_id)

    if user_id not in data:
        return False  # пользователь не найден

    data[user_id]["language"] = language

    save_users(data)
    return True


def is_user_logged_in(user_id):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(str(user_id))
    if not user:
        return False

    return user.get("logged_in", False)

def is_user_logged_in_fully(user_id):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(str(user_id))
    if not user:
        return False

    return user.get("logged_in_fully", False)

def set_user_logged_in_fully(user_id):
    with open("data/users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    user = users.get(str(user_id))
    if not user:
        return

    user["logged_in_fully"] = True

    with open("data/users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

async def handle_text(update, context):
    user = update.effective_user
    text = update.message.text
    existing_user = get_user(user.id)

    # ✅ разрешённые команды без логина
    allowed = ["🇬🇧 English", "🇷🇺 Русский", "/start"]

    # ❌ если не залогинен → редирект в start()
    if text not in allowed:
        if not (existing_user and existing_user.get("logged_in")):
            await start(update, context)
            return
        

    if (existing_user and not existing_user.get("logged_in_fully")):
        await send_welcome(update, user.id) 
        return
        

    if text == "🇷🇺 Русский":
        was_logged_in = is_user_logged_in(user.id)

        if not was_logged_in:
            login_user(user.id, user.username, "ru")
        else:
            set_user_language(user.id, "ru")

        if was_logged_in:
            msg = await send_dashboard(update, user.id)
        else:
            msg = await send_welcome(update, user.id)

        # 💾 безопасное сохранение message_id
        if msg and hasattr(msg, "message_id"):
            set_last_message_id(user.id, msg.message_id)
        else:
            print(f"[INFO] No message_id for user {user.id} (ru)")


    elif text == "🇬🇧 English":
        was_logged_in = is_user_logged_in(user.id)

        if not was_logged_in:
            login_user(user.id, user.username, "en")
        else:
            set_user_language(user.id, "en")

        if was_logged_in:
            msg = await send_dashboard(update, user.id)
        else:
            msg = await send_welcome(update, user.id)

        # 💾 безопасное сохранение message_id
        if msg and hasattr(msg, "message_id"):
            set_last_message_id(user.id, msg.message_id)
        else:
            print(f"[INFO] No message_id for user {user.id} (en)")



    elif text in [
        "Продолжить ➡️", "Continue ➡️",
        "💼 Мой баланс", "💼 My Balance",
        "Начать зарабатывать! ➡️", "Start Earning! ➡️",
        "/wallet"
    ]:

        is_fully_logged = is_user_logged_in_fully(user.id)

        if not is_fully_logged:
            set_user_logged_in_fully(user.id)

        last_message_id = get_last_message_id(user.id)

        # 🟢 Удаляем старое сообщение (если есть)
        if last_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=last_message_id
                )
            except Exception as e:
                print("Ошибка удаления:", e)

        # 🔥 Если уже залогинен → dashboard
        if is_fully_logged:
            msg = await send_dashboard(update, user.id)
            set_last_message_id(user.id, msg.message_id)

        # 🔵 Если нет → отправляем слайд
        else:
            await send_welcome(update, user.id) 



    elif text in ["🤑 Monthly Profit", "🤑 Доход за месяц"]:
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

        msg = await send_Monthly_Profit(update, user.id)
        set_last_message_id(user.id, msg.message_id)

    elif text in ["⚠️ Risks", "⚠️ Риски"]:

        keyboard = [
            [t("balance_button", user.id)]
        ]

        caption = t("risks_description", user.id)

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
            photo=open("images/Risks.jpg", "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        set_last_message_id(user.id, msg.message_id)

    elif text in ["💳 Deposit", "💳 Пополнить"]:

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

        set_last_message_id(user.id, msg.message_id)

    elif text in ["💸 Вывести", "💸 Withdraw"]:

        keyboard = [
            [t("balance_button", user.id)]
        ]

        caption = t("withdraw_text", user.id)

        last_message_id = get_last_message_id(user.id)

        # 🟢 Если есть сообщение → удаляем
        if last_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=last_message_id
                )
            except Exception as e:
                print("Ошибка удаления:", e)

        # 🔵 Отправляем новое (всегда)
        msg = await update.message.reply_photo(
            photo=open("images/Withdraw.jpg", "rb"),
            caption=caption,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

        set_last_message_id(user.id, msg.message_id)

    elif text in ["ℹ️ Мой бот", "ℹ️ My bot"]:
        keyboard = [
            [t("continue_button2", user.id)]
        ]
        await update.message.reply_photo(
            photo=open("images/Proof.jpg", "rb"),
            caption=t("slide_1_text", user.id),
            parse_mode="HTML",
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    elif text in ["Далее ➡️", "Next ➡️"]:
        keyboard = [
            [t("continue_button3", user.id)]
        ]
        await update.message.reply_photo(
            photo=open("images/Balance.jpg", "rb"),
            caption=t("slide_2_text", user.id),
            parse_mode="HTML",
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        
    elif text in ["Вау! ➡️", "Wow! ➡️"]:
        keyboard = [
            [t("continue_button4", user.id)]
        ]

        image_path = get_image("balance", user.id)

        with open(image_path, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=t("slide_3_text", user.id),
                parse_mode="HTML",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
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


async def handle_callback(update, context):
    query = update.callback_query
    user = query.from_user

    await query.answer()
    data = query.data

    print("Callback:", data)

    # 👉 START QUIZ
    if data.startswith("start_quiz"):
        keyboard = [
            [InlineKeyboardButton(t("answer_1_to_question_1", user.id), callback_data="q1_a1")],
            [InlineKeyboardButton(t("answer_2_to_question_1", user.id), callback_data="q1_a2")],
            [InlineKeyboardButton(t("answer_3_to_question_1", user.id), callback_data="q1_a3")],
            [InlineKeyboardButton(t("answer_4_to_question_1", user.id), callback_data="q1_a4")]
        ]

        try:
            await query.message.delete()
        except:
            pass

        await context.bot.send_photo(
            chat_id=user.id,
            photo=open("images/image.png", "rb"),
            caption=t("question_1", user.id),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 👉 Q1 → Q2
    elif data.startswith("q1_"):
        keyboard = [
            [InlineKeyboardButton(t("answer_1_to_question_2", user.id), callback_data="q2_a1")],
            [InlineKeyboardButton(t("answer_2_to_question_2", user.id), callback_data="q2_a2")],
            [InlineKeyboardButton(t("answer_3_to_question_2", user.id), callback_data="q2_a3")],
            [InlineKeyboardButton(t("answer_4_to_question_2", user.id), callback_data="q2_a4")]
        ]

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("images/image.png", "rb"),
                caption=t("question_2", user.id),
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 👉 Q2 → Q3
    elif data.startswith("q2_"):
        keyboard = [
            [InlineKeyboardButton(t("answer_1_to_question_3", user.id), callback_data="q3_a1")],
            [InlineKeyboardButton(t("answer_2_to_question_3", user.id), callback_data="q3_a2")],
            [InlineKeyboardButton(t("answer_3_to_question_3", user.id), callback_data="q3_a3")],
            [InlineKeyboardButton(t("answer_4_to_question_3", user.id), callback_data="q3_a4")]
        ]

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("images/image.png", "rb"),
                caption=t("question_3", user.id),
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 👉 Q3 → Q4
    elif data.startswith("q3_"):
        keyboard = [
            [InlineKeyboardButton(t("answer_1_to_question_4", user.id), callback_data="q4_a1")],
            [InlineKeyboardButton(t("answer_2_to_question_4", user.id), callback_data="q4_a2")],
            [InlineKeyboardButton(t("answer_3_to_question_4", user.id), callback_data="q4_a3")],
            [InlineKeyboardButton(t("answer_4_to_question_4", user.id), callback_data="q4_a4")]
        ]

        await query.message.edit_media(
            media=InputMediaPhoto(
                media=open("images/image.png", "rb"),
                caption=t("question_4", user.id),
                parse_mode="HTML"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 👉 FINISH
    elif data.startswith("q4_"):
        try:
            await query.message.delete()
        except:
            pass

        await query.message.reply_text(
            t("finnaly_5_", user.id),
            parse_mode="HTML"
        )
        # ⏳ задержка 2 секунды
        await asyncio.sleep(2)

        msg = await send_dashboard2(query.message, user.id)

        if msg and hasattr(msg, "message_id"):
            set_last_message_id(user.id, msg.message_id)



async def send_welcome(update, user_id):
    keyboard = [
        [InlineKeyboardButton(t("buttons_q", user_id)[0], callback_data="start_quiz")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # 👉 1. убираем клавиатуру
    await update.message.reply_text(
        text=t("setup_text", user_id),
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_photo(
        photo=open("images/Prew.jpg", "rb"),
        caption=t("welcome_text", user_id),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

def get_dashboard_keyboard(user_id):
    keyboard = [
        [
            t("dashboard_buttons1", user_id)[0],
            t("dashboard_buttons1", user_id)[1],
        ],
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


def get_monthly_profit_keyboard(user_id):
    keyboard = [
        [t("balance_button", user_id)]
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

    # 📁 Абсолютный путь к папке fonts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path_regular = os.path.abspath("fonts/ttf/DejaVuSans.ttf")
    font_path_bold = os.path.abspath("fonts/ttf/DejaVuSans-Bold.ttf")

    # 🔤 Шрифты
    try:
        font_title = ImageFont.truetype(font_path_regular, 36)
        font_big = ImageFont.truetype(font_path_bold, 70)
        font_small = ImageFont.truetype(font_path_regular, 28)
    except Exception as e:
        print("Ошибка загрузки шрифта:", e)
        font_title = ImageFont.load_default()
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 📊 Заголовок
    title_text = t("assets_overview", user_id)
    draw.text(
        (60, 50),
        title_text.replace("<b>", "").replace("</b>", ""),
        fill=(160, 180, 210),
        font=font_title
    )

    # 💰 Баланс
    draw.text(
        (60, 130),
        f"{balance:,.2f} USD$",
        fill=(255, 255, 255),
        font=font_big
    )

    # 📈 P&L
    pnl_color = (0, 200, 120) if pnl >= 0 else (255, 80, 80)
    pnl_sign = "+" if pnl >= 0 else ""

    initial_balance = balance - pnl
    percent = (pnl / initial_balance * 100) if initial_balance != 0 else 0

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

    draw.text(
        (60, 350),
        acc_text,
        fill=(120, 140, 180),
        font=font_small
    )

    # 💾 Сохранение
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes

async def send_dashboard(update, user_id):
    user = get_user_data(user_id)

    balance = user.get("balance", 0.0)
    pnl = user.get("P&L", 0.0)

    image = generate_balance_image(balance, pnl, user_id)

    msg = await update.message.reply_photo(
        photo=image,
        caption=t("update_info", user_id),
        parse_mode="HTML",
        reply_markup=get_dashboard_keyboard(user_id)
    )

    return msg  # 🔥 ВАЖНО


async def send_dashboard2(message, user_id):

    is_fully_logged = is_user_logged_in_fully(user_id)

    if not is_fully_logged:
        set_user_logged_in_fully(user_id)
        
    user = get_user_data(user_id)

    balance = user.get("balance", 0.0)
    pnl = user.get("P&L", 0.0)

    image = generate_balance_image(balance, pnl, user_id)

    msg = await message.reply_photo(
        photo=image,
        caption=t("update_info", user_id),
        parse_mode="HTML",
        reply_markup=get_dashboard_keyboard(user_id)
    )

    return msg


def generate_monthly_profit_image(balance, user_id):

    width, height = 900, 720
    img = Image.new("RGB", (width, height), color=(3, 12, 30))
    draw = ImageDraw.Draw(img)

    # 📁 Шрифты
    font_path_regular = os.path.abspath("fonts/ttf/DejaVuSans.ttf")
    font_path_bold = os.path.abspath("fonts/ttf/DejaVuSans-Bold.ttf")

    try:
        font_title = ImageFont.truetype(font_path_regular, 34)
        font_small = ImageFont.truetype(font_path_regular, 20)
        font_bold = ImageFont.truetype(font_path_bold, 24)
    except:
        font_title = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # 📊 Заголовок
    title = t("growth_projection", user_id)
    draw.text((60, 30), title, fill=(160, 180, 210), font=font_title)

    # 📈 настройки
    total_weeks = 20  # 5 месяцев
    growth = 1.05     # 5% в неделю

    # 📈 генерация данных
    def generate_values(start):
        values = [start]
        for _ in range(total_weeks):
            values.append(values[-1] * growth)
        return values

    user_values = generate_values(balance)

    base_compare = max(balance * 2, balance + 500)
    high_compare = max(base_compare * 3, base_compare + 100)

    demo_values = generate_values(base_compare)
    high_values = generate_values(high_compare)

    # 📐 график
    graph_x1, graph_y1 = 80, 120
    graph_x2, graph_y2 = 840, 520

    draw.rectangle([graph_x1, graph_y1, graph_x2, graph_y2], outline=(50, 70, 100))

    # 📊 масштаб
    all_values = user_values + demo_values + high_values
    max_value = max(all_values)
    min_value = -max_value * 0.05

    def get_xy(index, value):
        x = graph_x1 + (index / total_weeks) * (graph_x2 - graph_x1)
        y = graph_y2 - ((value - min_value) / (max_value - min_value)) * (graph_y2 - graph_y1)
        return x, y

    # 📍 линии месяцев
    for m in range(1, 6):
        week_index = m * 4
        x, _ = get_xy(week_index, 0)

        draw.line(
            [(x, graph_y1), (x, graph_y2)],
            fill=(80, 100, 140),
            width=1
        )

        draw.text(
            (x - 40, graph_y1 - 25),
            f"{m} {t('month_short', user_id)}",
            fill=(140, 160, 200),
            font=font_small
        )

    # 📈 линии
    user_points = [get_xy(i, v) for i, v in enumerate(user_values)]
    demo_points = [get_xy(i, v) for i, v in enumerate(demo_values)]
    high_points = [get_xy(i, v) for i, v in enumerate(high_values)]

    draw.line(user_points, fill=(0, 200, 120), width=4)
    draw.line(demo_points, fill=(80, 160, 255), width=3)
    draw.line(high_points, fill=(255, 140, 40), width=4)

    # 🔘 точки
    for p in user_points:
        draw.ellipse((p[0]-3, p[1]-3, p[0]+3, p[1]+3), fill=(0, 255, 150))

    for p in demo_points:
        draw.ellipse((p[0]-2, p[1]-2, p[0]+2, p[1]+2), fill=(120, 180, 255))

    for p in high_points:
        draw.ellipse((p[0]-2, p[1]-2, p[0]+2, p[1]+2), fill=(255, 200, 120))

    # 📅 X ось
    week_label = t("week_short", user_id)
    for i in range(0, total_weeks + 1, 2):
        x, _ = get_xy(i, 0)
        draw.text((x-10, graph_y2 + 10), f"{i}{week_label}", fill=(120, 140, 180), font=font_small)

    # 💰 Y ось
    steps = 6
    for i in range(steps + 1):
        val = min_value + (max_value - min_value) * i / steps
        y = graph_y2 - (i / steps) * (graph_y2 - graph_y1)
        draw.text((20, y-8), f"{int(max(val,0))}$", fill=(120, 140, 180), font=font_small)

    # 📌 ЛЕГЕНДА В СТОЛБИК 👇
    legend_y = 580
    gap = 30

    # 📈 финальные значения через 5 месяцев (20 недель)
    final_user = balance * (1.05 ** 20)
    final_demo = base_compare * (1.05 ** 20)
    final_high = high_compare * (1.05 ** 20)

    # 📌 легенда (с прогнозом)
    draw.text((80, legend_y), 
        f"● {t('your_balance_label', user_id)} "
        f"({int(balance)}$ → {int(final_user)}$ {t('in_5_months', user_id)})",
        fill=(0, 200, 120), font=font_small)

    draw.text((80, legend_y + gap), 
        f"● {t('start_deposit_label', user_id)} "
        f"({int(base_compare)}$ → {int(final_demo)}$ {t('in_5_months', user_id)})",
        fill=(120, 180, 255), font=font_small)

    draw.text((80, legend_y + gap*2), 
        f"● {t('advanced_deposit_label', user_id)} "
        f"({int(high_compare)}$ → {int(final_high)}$ {t('in_5_months', user_id)})",
        fill=(255, 140, 40), font=font_small)

    # 💾 сохранить
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes


async def send_Monthly_Profit(update, user_id):
    user = get_user_data(user_id)
    balance = user.get("balance", 0.0)

    image = generate_monthly_profit_image(balance, user_id)

    msg = await update.message.reply_photo(
        photo=image,
        caption=t("monthly_growth_description", user_id),
        parse_mode="HTML",
        reply_markup=get_monthly_profit_keyboard(user_id)
    )

    return msg