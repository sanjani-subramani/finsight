from collections.abc import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.platform.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except HTTPException:
            # An HTTPException is a deliberate "return this error response"
            # decision, not a DB failure — e.g. incrementing a failed-login
            # counter before rejecting with 401, or revoking a stolen
            # refresh-token chain before rejecting a reuse attempt. Those
            # writes are intentional and must survive the error response,
            # so we commit here instead of discarding them.
            await session.commit()
            raise
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
