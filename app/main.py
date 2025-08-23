from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router as api_router
from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import init_db

# Configure logging
configure_logging()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="SayWrite Local API",
    description="Local API for speech-to-text and text rewriting",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/v1")
app.include_router(auth_router, prefix="/v1/auth")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
    )
