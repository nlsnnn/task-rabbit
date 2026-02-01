from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


class DatabaseHelper:
    def __init__(self, url: str):
        self._engine = create_async_engine(
            url=url,
            echo=False,
            echo_pool=False,
            pool_size=20,
            max_overflow=40,
            pool_timeout=30,
        )
        self.session_maker = async_sessionmaker(
            bind=self._engine, autoflush=False, expire_on_commit=False
        )

    async def dispose(self):
        await self._engine.dispose()

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


db_helper = DatabaseHelper(url=settings.db.url)
