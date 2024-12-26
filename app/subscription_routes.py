from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timedelta
from app.database import get_session
from app.models import Subscriptions
from pydantic import BaseModel


# Класс для создания подписки
class CreateSubscriptionRequest(BaseModel):
    user_id: int  # Идентификатор пользователя
    duration_days: int  # Длительность подписки в днях


# Создаем экземпляр маршрутизатора FastAPI
router = APIRouter()


@router.post("/create/")
async def create_subscription(
    request: CreateSubscriptionRequest,  # Используем модель для запроса
    session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт для создания новой подписки.

    :param request: Тело запроса с данными о подписке.
    :param session: Асинхронная сессия базы данных.
    :return: Сообщение об успешном создании подписки и информация о подписке.
    """
    # Доступ к данным через объект `request`
    user_id = request.user_id
    duration_days = request.duration_days

    # Определяем дату начала и окончания подписки
    start_date = datetime.now()
    end_date = start_date + timedelta(days=duration_days)

    # Создаем новую подписку
    new_subscription = Subscriptions(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status="active"
    )

    # Добавляем новую подписку в сессию и сохраняем изменения
    session.add(new_subscription)
    await session.commit()

    # Возвращаем сообщение об успешном создании и информацию о подписке
    return {"message": "Subscription created successfully", "subscription": new_subscription}


@router.put("/update/{subscription_id}/")
async def update_subscription(
    subscription_id: int,
    request: CreateSubscriptionRequest,  # Используем модель для запроса
    session: AsyncSession = Depends(get_session)
):
    """
    Эндпоинт для обновления существующей подписки.

    :param subscription_id: Идентификатор подписки, которую нужно обновить.
    :param request: Тело запроса с новыми данными для обновления.
    :param session: Асинхронная сессия базы данных.
    :return: Сообщение об успешном обновлении подписки и информация о подписке.
    """
    # Выполняем запрос к базе данных для поиска подписки по subscription_id
    query = select(Subscriptions).where(Subscriptions.id == subscription_id)
    result = await session.execute(query)

    # Извлекаем первую найденную подписку
    subscription = result.scalars().first()

    # Если подписка не найдена, возвращаем ошибку 404
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Обновляем данные подписки
    subscription.user_id = request.user_id
    subscription.end_date = datetime.now() + timedelta(days=request.duration_days)

    # Сохраняем изменения в базе данных
    await session.commit()

    # Возвращаем сообщение об успешном обновлении и информацию о подписке
    return {"message": "Subscription updated successfully", "subscription": subscription}


@router.get("/status/")
async def subscription_status(user_id: int, session: AsyncSession = Depends(get_session)):
    """
    Эндпоинт для проверки статуса подписки пользователя.

    :param user_id: Идентификатор пользователя для проверки статуса подписки.
    :param session: Асинхронная сессия базы данных.
    :return: Информация о подписке.
    """
    # Выполняем запрос к базе данных для поиска подписки по user_id
    query = select(Subscriptions).where(Subscriptions.user_id == user_id)
    result = await session.execute(query)

    # Извлекаем первую найденную подписку
    subscription = result.scalars().first()

    # Если подписка не найдена, возвращаем ошибку 404
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Возвращаем информацию о подписке
    return subscription