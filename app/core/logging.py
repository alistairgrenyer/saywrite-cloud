import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import Processor

from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog for the application."""
    
    # Set up structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    # Add console renderer for development
    if settings.LOG_LEVEL != "DEBUG":
        # In production, use JSON renderer
        processors.append(structlog.processors.JSONRenderer())
    else:
        # In development, use console renderer
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Set log level
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL)
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger instance for the given name."""
    return structlog.get_logger(name)


def redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact sensitive data from logs if redaction is enabled.
    
    Args:
        data: Dictionary containing data that might include sensitive information
        
    Returns:
        Dictionary with sensitive data redacted if redaction is enabled
    """
    if not settings.ENABLE_REDACTION:
        return data
    
    result = data.copy()
    sensitive_keys = [
        "api_key", "key", "token", "secret", "password", "authorization",
        "transcript", "text", "content", "draft"
    ]
    
    for key in result:
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(result[key], str):
                result[key] = "[REDACTED]"
    
    return result
