import asyncio
import os

from config import YOOMONEY_TOKEN, RECEIVER
from yoomoney import Quickpay, Client

# Проверяем, что RECEIVER не пустой
if not RECEIVER:
    raise ValueError("RECEIVER is not set in .env file")

# Создание ссылки на оплату
def create_payment(amount: float, user_id: int, label: str) -> str:
    quickpay = Quickpay(
        receiver=RECEIVER,
        quickpay_form="shop",
        targets="Subscription Payment",
        paymentType="AC",  # Оплата картой
        sum=amount,
        label=label
    )
    return quickpay.redirected_url

# Проверка статуса платежа (асинхронная версия)
async def check_payment_status(label: str) -> dict:
    client = Client(YOOMONEY_TOKEN)

    # Ожидаем выполнения синхронного кода в отдельном потоке
    operations = await asyncio.to_thread(client.operation_history, label=label)

    # Ищем нужную операцию
    for operation in operations.operations:
        if operation.label == label:
            return {
                "status": operation.status,
                "amount": operation.amount,
                "datetime": operation.datetime,
                "title": operation.title
            }
    return None