from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy import Boolean, Column, DateTime, text
from datetime import datetime, timezone
from sqlalchemy.ext.declarative import as_declarative
from fastapi import HTTPException, status

from app.core.config import settings

# Create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# Create declarative base for models
@as_declarative()
class BaseModel:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted = Column(Boolean, default=False)

    @staticmethod
    def soft_delete(mapper, connection, target):
        target.deleted = True
        target.updated_at = datetime.now(timezone.utc)


event.listen(BaseModel, 'before_delete', BaseModel.soft_delete)


async def init_db():
    """Initialize database connection"""
    # Alembic migrations handle table creation
    pass


async def close_db():
    """Close database connection"""
    await engine.dispose()


# Dependency to get DB session
async def get_db():
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        # Proactively verify DB connectivity to fail fast with a clean 503
        try:
            await session.execute(text("SELECT 1"))
        except Exception as e:
            # Ensure no transaction state is left dangling
            try:
                await session.rollback()
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="SayWrite is unavailable. Please try again later.",
            ) from e

        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
