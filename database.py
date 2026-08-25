import logging
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.models import Base

log = logging.getLogger(__name__)
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    log.info("Database initialized")


async def session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as database:
        yield database


async def close_database() -> None:
    await engine.dispose()