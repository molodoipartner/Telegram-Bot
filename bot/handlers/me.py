from bot.services.user_service import get_user

async def me(update, context):
    user = update.effective_user

    user_data = get_user(user.id)

    if user_data:
        text = f"Ты: {user_data['username']}\nСтатус: залогинен\nЯзык: {user_data.get('language', 'Не установлен')}"
    else:
        text = "Ты не залогинен ❌"

    await update.message.reply_text(text)