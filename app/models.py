from sqlmodel import SQLModel, Field, Column, TIMESTAMP, ForeignKey
from datetime import datetime, UTC

# Базовая модель для электронной почты
class UsersEmail(SQLModel):
    email: str

# Модель для входа пользователя
class UsersLogin(UsersEmail):
    password: str

# Базовая информация о пользователе
class UsersBase(UsersEmail):
    name: str

# Модель для регистрации пользователя
class UsersRegister(UsersBase):
    password: str

# Публичная модель пользователя (для возврата в API)
class UsersPublic(UsersBase):
    id: int
    date_joined: datetime

# Таблица пользователей (в схеме public)
class Users(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    hashed_password: str
    date_joined: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(TIMESTAMP(timezone=True)),
    )

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