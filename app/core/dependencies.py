from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import verify_token
from app.services.auth.user_service import UserService
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.core.database import get_db
from app.models.api.schemas import User

# Security scheme
security = HTTPBearer()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get user service with injected repository."""
    user_repository = SQLAlchemyUserRepository(db)
    return UserService(user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials, credentials_exception)
    user = await user_service.get_user_by_email(email=token_data.email)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
