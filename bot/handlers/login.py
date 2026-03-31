from bot.services.user_service import save_user

async def login(update, context):
    user = update.effective_user

    save_user(user.id, user.username)

    await update.message.reply_text("Ты залогинен ✅")