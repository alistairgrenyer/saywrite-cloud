from typing import Optional
from app.models.api.schemas import User, UserCreate
from app.repositories.user_repository import UserRepositoryInterface


class UserService:
    """Service for user management with dependency injection."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self.user_repository.create_user(user_data)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        return await self.user_repository.authenticate_user(email, password)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repository.get_user_by_email(email)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.get_user_by_id(user_id)
