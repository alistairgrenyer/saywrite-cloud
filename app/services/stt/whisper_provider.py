import os
import time
from pathlib import Path
from typing import Optional, Tuple

from openai import OpenAI

from app.core.config import settings
from app.core.logging import get_logger

# Create logger
logger = get_logger(__name__)


class WhisperSTT:
    """Speech-to-text service using OpenAI Whisper API."""
    
    def __init__(self):
        """Initialize the Whisper API client."""
        self._client = None
        self._model = settings.WHISPER_MODEL
        logger.info("Initializing Whisper STT service", model=self._model)
    
    @property
    def client(self) -> OpenAI:
        """
        Lazy-load the OpenAI client when first needed.
        
        Returns:
            OpenAI: The OpenAI client.
        """
        if self._client is None:
            if not settings.WHISPER_API_KEY:
                # If WHISPER_API_KEY is not set, try to use OPENAI_API_KEY
                api_key = settings.OPENAI_API_KEY
                if not api_key:
                    raise ValueError("Neither WHISPER_API_KEY nor OPENAI_API_KEY is set")
            else:
                api_key = settings.WHISPER_API_KEY
            
            self._client = OpenAI(api_key=api_key)
            logger.info("Whisper API client initialized")
        
        return self._client
    
    async def transcribe(
        self, 
        audio_file: Path, 
        language: Optional[str] = None
    ) -> Tuple[str, int]:
        """
        Transcribe audio file to text using OpenAI Whisper API.
        
        Args:
            audio_file: Path to audio file
            language: Optional language hint
            
        Returns:
            Tuple containing transcribed text and processing time in milliseconds
        """
        start_time = time.time()
        
        logger.info(
            "Transcribing audio file with Whisper API", 
            file=str(audio_file),
            language=language
        )
        
        try:
            with open(audio_file, "rb") as audio:
                # Call Whisper API
                response = self.client.audio.transcriptions.create(
                    model=self._model,
                    file=audio,
                    language=language
                )
            
            # Extract transcribed text
            transcribed_text = response.text
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "Transcription completed",
                processing_time_ms=processing_time_ms
            )
            
            return transcribed_text, processing_time_ms
            
        except Exception as e:
            logger.exception("Error transcribing audio", error=str(e))
            raise


# Create a singleton instance
whisper_stt = WhisperSTT()
