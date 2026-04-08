from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes


async def test_deposit(update, context):
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Deposit",
        description="Пополнение баланса",
        payload="deposit_payload",
        provider_token="1877036958:TEST:1152d2bb0d51a20b4b53a19d91eae5278eff9137",
        currency="USD",  # или EUR
        prices=[{"label": "Balance", "amount": 500}],  # 5.00$
        start_parameter="deposit"
    )