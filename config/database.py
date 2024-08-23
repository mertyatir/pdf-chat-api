from .logger import logger
import os

from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://myuser:mypassword@localhost:5432/pdf_chat_db",
)


async_engine = create_async_engine(
    DATABASE_URL, echo=False, poolclass=NullPool
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """Get a database session.

    To be used for dependency injection.
    """
    async with async_session() as session, session.begin():
        logger.info("Creating a new database session")
        yield session
