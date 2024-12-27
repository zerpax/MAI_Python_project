from typing import Optional, List

from sqlalchemy import JSON
from sqlmodel import SQLModel, Field, Column, TIMESTAMP
from datetime import datetime, UTC


#user
class UsersEmail(SQLModel):
    email: str


class UsersLogin(UsersEmail):
    password: str


class UsersBase(UsersEmail):
    name: str


class UsersRegister(UsersBase):
    password: str


class Users(UsersBase, table=True):
    __tablename__ = 'users'
    id: int | None = Field(default=None, primary_key=True)
    date_joined: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_column=Column(TIMESTAMP(timezone=True))
    )
    hashed_password: str


class UsersPublic(UsersBase):
    id: int
    date_joined: datetime

#history
class VisitBase(SQLModel):
    site_id: int
    time: str


class VisitPublic(VisitBase):
    ip_address: str


class History(SQLModel, table=True):
    __tablename__ = 'history'
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(default=None)
    history: List[dict] = Field(default=[], sa_column=Column(JSON))  # Храним историю как JSON


class ScammerPublic(SQLModel):
    ip_address: str


class Scammers(SQLModel, table=True):
    __tablename__ = 'scammers'
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(default=None, unique=True)


#Subsciptions
# Таблица платежей (в схеме public)
class Payments(SQLModel, table=True):
    __tablename__ = "payments"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")  # Внешний ключ на таблицу пользователей
    amount: float  # Сумма платежа
    status: str  # Статус платежа: pending, success, failed
    payment_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True)),
    )
    payment_id: str  # Идентификатор платежа в системе

# Таблица подписок (в схеме public)
class Subscriptions(SQLModel, table=True):
    __tablename__ = "subscriptions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")  # Внешний ключ на таблицу пользователей
    start_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True)),
    )
    end_date: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))  # Конец подписки
    status: str  # Статус подписки: active, cancelled, expired



