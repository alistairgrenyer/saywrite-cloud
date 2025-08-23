from app.core.logging import get_logger
from app.services.llm.openai_provider import openai_provider

# Create logger
logger = get_logger(__name__)


def get_llm_provider():
    """
    Get the OpenAI LLM provider.
    
    Returns:
        The OpenAI LLM provider instance.
    """
    logger.info("Using OpenAI LLM provider")
    return openai_provider
