import logging

from collections.abc import AsyncGenerator
from typing import Any, Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import config
from models import Base

logger = logging.getLogger(__name__)
engine = create_async_engine(config.DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db:
        yield db

session = Annotated[AsyncSession, Depends(get_session)]


async def init_db(engine: Any = engine):
    async with engine.begin() as conn:
        logger.info("Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialization complete.")
