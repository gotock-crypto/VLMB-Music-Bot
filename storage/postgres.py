"""Isolated asynchronous PostgreSQL connection layer for VLMB."""
from __future__ import annotations

import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = os.getenv("VLMB_POSTGRES_URL", "").strip()

engine = (
    create_async_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )
    if DATABASE_URL
    else None
)

SessionFactory = (
    async_sessionmaker(engine, expire_on_commit=False)
    if engine is not None
    else None
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a PostgreSQL session when explicitly configured."""
    if SessionFactory is None:
        raise RuntimeError("VLMB_POSTGRES_URL is not configured")

    async with SessionFactory() as session:
        yield session


async def close_postgres() -> None:
    """Dispose the PostgreSQL engine if configured."""
    if engine is not None:
        await engine.dispose()
