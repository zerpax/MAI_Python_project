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


class Users(UsersBase, table=True, schema='user_data'):
    __tablename__ = 'users'
    # __table_args__ = {'schema': 'user_data'}
    id: int | None = Field(default=None, primary_key=True)
    date_joined: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_column=Column(TIMESTAMP(timezone=True))
    )
    hashed_password: str


class UsersPublic(UsersBase):
    id: int
    date_joined: datetime


#history
class History(SQLModel, table=True):
    __tablename__ = 'history'
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(default=None)
    history: List[dict] = Field(default=[], sa_column=Column(JSON))  # Храним историю как JSON
    # last_visited_index: Optional[int] = Field(default=None)


# def add_site(user_id: int, site_id: int, time: datetime):
#     """Добавляет новый сайт в историю, заменяя старые, если необходимо"""
#     # Получаем текущую историю посещений
#     query = select(History).where(History.id == user_id)
#     with get_session() as session:
#         history = session.execute(query).scalars().first().history
#
#         # Перезаписываем первый элемент, если история уже полная
#         if len(history) == 10:
#             history.pop(0)  # Удаляем старый сайт
#
#         # Добавляем новый сайт с временной меткой
#         history.append({"site": site_id, "time": time})
#
#         # Сохраняем изменения в базе данных
#         query = update(History).where(History.id == user_id).values(history=history)
#         session.execute(query)
#         session.commit()


class Scammers(SQLModel, table=True):
    __tablename__ = 'scammers'
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(default=None, unique=True)




