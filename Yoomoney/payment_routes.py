from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database import get_session
from models import Payments
from Yoomoney.yoomoney_utils import create_payment, check_payment_status
from pydantic import BaseModel

# Создаем экземпляр маршрутизатора FastAPI
router = APIRouter()

class CreatePaymentRequest(BaseModel):
    amount: float
    user_id: int

@router.post("/create/")
async def create_payment_endpoint(
    request: CreatePaymentRequest,  # Используем модель вместо отдельных параметров
    session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт для создания нового платежа.

    :param request: Тело запроса с данными о платеже.
    :param session: Асинхронная сессия базы данных.
    :return: URL для проведения платежа.
    """
    # Доступ к данным через объект `request`
    amount = request.amount
    user_id = request.user_id

    # Генерируем метку для платежа на основе идентификатора пользователя
    label = f"user_{user_id}_payment"

    # Создаем платеж через YooMoney и получаем URL для редиректа
    payment_url = create_payment(amount=amount, user_id=user_id, label=label)

    # Создаем запись нового платежа в базе данных
    new_payment = Payments(
        user_id=user_id,
        amount=amount,
        status="pending",
        payment_id=label
    )

    # Добавляем новый платеж в сессию и сохраняем изменения
    session.add(new_payment)
    await session.commit()

    # Возвращаем URL для оплаты
    return {"payment_url": payment_url}

@router.get("/status/")
async def check_payment_status_endpoint(payment_id: str, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для проверки статуса платежа.

    :param payment_id: Идентификатор платежа для проверки статуса.
    :param session: Асинхронная сессия базы данных.
    :return: Информация о статусе платежа.
    """
    # Выполняем запрос к базе данных для поиска платежа по его идентификатору
    payment_data = await session.execute(select(Payments).where(Payments.payment_id == payment_id))

    # Извлекаем первый найденный платеж
    payment = payment_data.scalars().first()

    # Если платеж не найден, возвращаем ошибку 404
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Проверяем статус платежа через YooMoney
    payment_info = await check_payment_status(label=payment_id)

    # Если информация о платеже найдена, обновляем статус в базе данных
    if payment_info:
        payment.status = payment_info['status']
        await session.commit()
        return payment_info

    # Если информация о платеже не найдена, возвращаем ошибку 400
    raise HTTPException(status_code=400, detail="Payment not found in YooMoney")


