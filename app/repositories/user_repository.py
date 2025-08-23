from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.database import UserModel
from app.models.schemas import User, UserCreate
from app.core.auth import get_password_hash


class UserRepositoryInterface(ABC):
    """Abstract interface for user repository."""
    
    @abstractmethod
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
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
            self.db.commit()
            self.db.refresh(db_user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email already exists")
        
        return self._model_to_schema(db_user)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user:
            return self._model_to_schema(db_user)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return self._model_to_schema(db_user)
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        from app.core.auth import verify_password
        
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if db_user and verify_password(password, db_user.hashed_password):
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
