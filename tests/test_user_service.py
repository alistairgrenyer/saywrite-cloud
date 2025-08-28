import pytest
from unittest.mock import Mock
from app.services.auth.user_service import UserService
from app.repositories.user_repository import UserRepositoryInterface
from app.models.api.schemas import User, UserCreate


class MockUserRepository(UserRepositoryInterface):
    """Mock repository for testing."""
    
    def __init__(self):
        self.users = {}
        self.next_id = 1
    
    def create_user(self, user_data: UserCreate) -> User:
        if any(user.email == user_data.email for user in self.users.values()):
            raise ValueError("User with this email already exists")
        
        user_id = str(self.next_id)
        self.next_id += 1
        
        user = User(
            id=user_id,
            email=user_data.email,
            is_active=True,
            created_at="2023-01-01T00:00:00"
        )
        self.users[user_id] = user
        return user
    
    def get_user_by_email(self, email: str) -> User | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)
    
    def authenticate_user(self, email: str, password: str) -> User | None:
        # Simple mock authentication
        user = self.get_user_by_email(email)
        if user and password == "correct_password":
            return user
        return None


class TestUserService:
    """Test cases for UserService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_repo = MockUserRepository()
        self.user_service = UserService(self.mock_repo)
    
    def test_create_user_success(self):
        """Test successful user creation."""
        user_data = UserCreate(email="test@example.com", password="password123")
        user = self.user_service.create_user(user_data)
        
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.id is not None
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email."""
        user_data = UserCreate(email="test@example.com", password="password123")
        self.user_service.create_user(user_data)
        
        with pytest.raises(ValueError, match="User with this email already exists"):
            self.user_service.create_user(user_data)
    
    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user_data = UserCreate(email="test@example.com", password="password123")
        created_user = self.user_service.create_user(user_data)
        
        authenticated_user = self.user_service.authenticate_user("test@example.com", "correct_password")
        assert authenticated_user is not None
        assert authenticated_user.email == created_user.email
    
    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials."""
        user_data = UserCreate(email="test@example.com", password="password123")
        self.user_service.create_user(user_data)
        
        authenticated_user = self.user_service.authenticate_user("test@example.com", "wrong_password")
        assert authenticated_user is None
    
    def test_get_user_by_email(self):
        """Test getting user by email."""
        user_data = UserCreate(email="test@example.com", password="password123")
        created_user = self.user_service.create_user(user_data)
        
        found_user = self.user_service.get_user_by_email("test@example.com")
        assert found_user is not None
        assert found_user.email == created_user.email
    
    def test_get_user_by_id(self):
        """Test getting user by ID."""
        user_data = UserCreate(email="test@example.com", password="password123")
        created_user = self.user_service.create_user(user_data)
        
        found_user = self.user_service.get_user_by_id(created_user.id)
        assert found_user is not None
        assert found_user.id == created_user.id
