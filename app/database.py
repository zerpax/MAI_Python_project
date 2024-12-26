from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from typing import AsyncGenerator

database_URL = "postgresql+asyncpg://ivan:postgres@localhost:5432/python_pr"
engine = create_async_engine(database_URL,  echo=True)
Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with Session() as session:
        yield session