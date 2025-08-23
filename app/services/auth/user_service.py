from typing import Optional
from app.models.schemas import User, UserCreate
from app.repositories.user_repository import UserRepositoryInterface


class UserService:
    """Service for user management with dependency injection."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return self.user_repository.create_user(user_data)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        return self.user_repository.authenticate_user(email, password)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repository.get_user_by_email(email)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.user_repository.get_user_by_id(user_id)
