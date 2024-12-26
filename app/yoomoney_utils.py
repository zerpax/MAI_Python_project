import asyncio
from yoomoney import Quickpay, Client

YOOMONEY_TOKEN = "4100118940251415.73747AF94C5DB397A0AA3C2A1FEFDD30DEB8DB519D056996192504FE2BB28925EC3865801328567DBCA1BF9D2E7E0A4A94C3C581805481DE29B25E5711E06BD35CA9B2D8B39CD6DBA9C0A607F9A9A0F82A46A38E271D557D98EA41277A175BBA8613106D7B067DD8BD3CFE4A5A7776554A0A57C332F5D59347D5C74B0DE477E0"
RECEIVER = "4100118940251415"  # Ваш номер кошелька

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