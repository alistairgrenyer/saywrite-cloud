from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import root_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.database import init_db, close_db
from app.core.logging import get_logger
from app.core.test_seeder import seed_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure logging
    configure_logging()
    logger = get_logger(__name__)
    
    # Startup: Initialize connections
    logger.info("Starting application...")
    await init_db()
    logger.info("Database initialized")

    # Seed database
    logger.info("Seeding initiated...")
    await seed_db()
    logger.info("Seeding completed")
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown: Clean up connections
    logger.info("Shutting down application...")
    await close_db()

# Create FastAPI app
app = FastAPI(
    title="SayWrite API",
    description="SayWrite API for speech-to-text and text rewriting",
    version="0.1.0",
    lifespan=lifespan,
    license_info={
            "name": "AGPL-3.0"
        }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost", 
        "http://localhost:*", 
        "https://app.saywrite.nously.io", 
        "https://app.saywrite.nously.io:*",
        "https://api.saywrite.nously.io",
        "https://api.saywrite.nously.io:*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(root_router, prefix="/api")

@app.get("/", tags=["default"])
async def root():
    return {"message": "Welcome to SayWrite API"}
