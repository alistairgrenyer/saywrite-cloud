from .routes import router as api_router
from .auth import router as auth_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(api_router)
router.include_router(auth_router, prefix="/auth")

__all__ = ["router"]
