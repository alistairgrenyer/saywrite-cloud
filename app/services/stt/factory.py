from app.core.config import settings
from app.core.logging import get_logger
from app.services.stt.whisper_provider import whisper_stt
from app.services.stt.faster_whisper import faster_whisper_stt

# Create logger
logger = get_logger(__name__)


def get_stt_provider():
    """
    Get the appropriate STT provider based on configuration.
    
    Returns:
        The STT provider instance (either OpenAI Whisper API or faster-whisper).
    """
    provider = settings.WHISPER_PROVIDER.lower()
    
    if provider == "local":
        logger.info("Using local faster-whisper STT provider")
        return faster_whisper_stt
    else:
        logger.info("Using OpenAI Whisper API STT provider")
        return whisper_stt
