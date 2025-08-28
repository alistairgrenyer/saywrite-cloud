from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import async_session
from app.services.auth.user_service import UserService
from app.models.api.schemas import UserCreate
from app.repositories.user_repository import SQLAlchemyUserRepository

logger = get_logger(__name__)

async def seed_db():
    logger.info("Seeding database...")
    async with async_session() as db:
        await seed_users(db)

async def seed_users(db: AsyncSession):
    logger.info("Seeding users...")

    user_service = UserService(SQLAlchemyUserRepository(db))

    try:
        user = UserCreate(email="test@example.com", password="password")
        await user_service.create_user(user)
        logger.info(f"User seeded successfully: {user.email}")
    except Exception:
        logger.error(f"Failed to seed user {user.email} - SKIPPING")
