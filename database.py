from typing import AsyncGenerator
from config import DATABASE_URL

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

database_URL = DATABASE_URL #связать с базой данных проекта
engine = create_async_engine(database_URL,  echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session