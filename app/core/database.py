from app.models.database import create_tables, engine
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_db():
    """Initialize the database by creating all tables."""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise


def check_db_connection():
    """Check if database connection is working."""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False
