from telegram import Update
from telegram.ext import ContextTypes

async def precheckout_callback(update, context):
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment(update, context):
    payment = update.message.successful_payment

    amount = payment.total_amount / 100
    currency = payment.currency

    await update.message.reply_text(
        f"✅ Оплата прошла!\nСумма: {amount} {currency}"
    )