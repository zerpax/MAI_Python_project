from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
from dotenv import load_dotenv
import os

# Загружаем данные из .env файла
load_dotenv()

# Используем данные из .env
database_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(database_URL, echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session