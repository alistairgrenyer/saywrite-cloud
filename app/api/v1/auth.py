from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.api import UserCreate, UserLogin, User, Token, TokenRefresh
from app.services.auth.user_service import UserService
from app.core.auth import create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import settings
from app.core.logging import get_logger
from app.core.dependencies import get_user_service

# Create logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/register", response_model=User, tags=["auth"])
async def register(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Register a new user.
    
    Args:
        user_data: User registration data (email and password)
        
    Returns:
        User: The created user information
    """
    logger.info("User registration attempt", email=user_data.email)
    
    try:
        user = await user_service.create_user(user_data)
        logger.info("User registered successfully", user_id=user.id, email=user.email)
        return user
    except ValueError as e:
        logger.warning("Registration failed", email=user_data.email, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token, tags=["auth"])
async def login(
    user_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
) -> Token:
    """
    Login user and return JWT token.
    
    Args:
        user_data: User login credentials (email and password)
        
    Returns:
        Token: JWT access token
    """
    logger.info("User login attempt", email=user_data.email)
    
    user = await user_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        logger.warning("Login failed - invalid credentials", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    user.refresh_token = refresh_token
    await user_service.update_user(user.id, user)
    
    logger.info("User logged in successfully", user_id=user.id, email=user.email)
    return TokenRefresh(access_token=access_token, refresh_token=refresh_token, token_type="bearer", expires_in=access_token_expires.total_seconds())


@router.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
) -> Token:
    """
    OAuth2 compatible token login endpoint.
    
    Args:
        form_data: OAuth2 form data with username (email) and password
        
    Returns:
        Token: JWT access token
    """
    logger.info("OAuth2 token request", username=form_data.username)
    
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning("OAuth2 login failed - invalid credentials", username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    logger.info("OAuth2 token issued successfully", user_id=user.id, email=user.email)
    return Token(access_token=access_token, token_type="bearer", expires_in=access_token_expires.total_seconds())


@router.post("/refresh_token", response_model=Token, tags=["auth"])
async def refresh_token(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service)
) -> Token:
    """
    Refresh JWT access token using a refresh token.
    
    Args:
        refresh_token: Refresh token
        
    Returns:
        Token: JWT access token
    """
    logger.info("Refresh token request", refresh_token=refresh_token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_refresh_token(refresh_token, credentials_exception)
    user = await user_service.get_user_by_email(email=token_data.email)
    if not user:
        logger.warning("Refresh token failed - invalid credentials", email=token_data.email)
        raise credentials_exception
    if user.refresh_token != refresh_token:
        logger.warning("Refresh token failed - invalid refresh token", email=token_data.email)
        raise credentials_exception
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    logger.info("Refreshed access token issued successfully", user_id=user.id, email=user.email)
    return Token(access_token=access_token, token_type="bearer", expires_in=access_token_expires.total_seconds())
