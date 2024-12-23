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
    __table_args__ = {'schema': 'user_data'}
    id: int | None = Field(default=None, primary_key=True)
    date_joined: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_column=Column(TIMESTAMP(timezone=True))
    )
    hashed_password: str


class UsersPublic(UsersBase):
    id: int
    date_joined: datetime


