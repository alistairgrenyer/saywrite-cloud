from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.db import UserModel
from app.models.api.schemas import User, UserCreate
from app.core.auth import get_password_hash


class UserRepositoryInterface(ABC):
    """Abstract interface for user repository."""
    
    @abstractmethod
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user_data: User) -> Optional[User]:
        """Update user by ID."""
        pass


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user model
        db_user = UserModel(
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        try:
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("User with this email already exists")
        
        return self._model_to_schema(db_user)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(UserModel).filter(UserModel.email == email))
        db_user = result.scalar_one_or_none()
        if db_user:
            return self._model_to_schema(db_user)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            return self._model_to_schema(db_user)
        return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        from app.core.auth import verify_password
        
        result = await self.db.execute(select(UserModel).filter(UserModel.email == email))
        db_user = result.scalar_one_or_none()
        if db_user and verify_password(password, db_user.hashed_password):
            return self._model_to_schema(db_user)
        return None

    async def update_user(self, user_id: str, user_data: User) -> Optional[User]:
        """Update user by ID."""
        result = await self.db.execute(select(UserModel).filter(UserModel.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            # Only update allowed mutable fields
            payload = user_data.model_dump(exclude_unset=True)
            allowed_fields = {"email", "is_active", "refresh_token"}
            for field in allowed_fields:
                if field in payload:
                    setattr(db_user, field, payload[field])
            await self.db.commit()
            await self.db.refresh(db_user)
            return self._model_to_schema(db_user)
        return None
    
    def _model_to_schema(self, db_user: UserModel) -> User:
        """Convert database model to Pydantic schema."""
        return User(
            id=str(db_user.id),
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at.isoformat()
        )
