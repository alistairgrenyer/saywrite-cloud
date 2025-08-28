from .v1 import router as v1_router
from fastapi import APIRouter

root_router = APIRouter()
root_router.include_router(v1_router, prefix="/v1")

__all__ = ["root_router"]
