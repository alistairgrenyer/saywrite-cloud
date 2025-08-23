import os
import time
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from faster_whisper import WhisperModel

from app.core.config import settings
from app.core.logging import get_logger

# Create logger
logger = get_logger(__name__)


class FasterWhisperSTT:
    """Speech-to-text service using faster-whisper."""
    
    def __init__(self):
        """Initialize the faster-whisper model."""
        self._model = None
        self._model_name = settings.WHISPER_MODEL
        self._compute_type = settings.WHISPER_COMPUTE_TYPE
        logger.info(
            "Initializing faster-whisper STT service", 
            model=self._model_name, 
            compute_type=self._compute_type
        )
    
    @property
    def model(self) -> WhisperModel:
        """
        Lazy-load the model when first needed.
        
        Returns:
            WhisperModel: The loaded faster-whisper model.
        """
        if self._model is None:
            logger.info("Loading faster-whisper model", model=self._model_name)
            self._model = WhisperModel(
                model_size_or_path=self._model_name,
                device="cpu",
                compute_type=self._compute_type,
            )
            logger.info("Model loaded successfully")
        return self._model
    
    async def transcribe(
        self, 
        audio_file: Path, 
        language: Optional[str] = None
    ) -> Tuple[str, int]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            language: Optional language hint
            
        Returns:
            Tuple containing transcribed text and processing time in milliseconds
        """
        start_time = time.time()
        
        logger.info(
            "Transcribing audio file", 
            file=str(audio_file),
            language=language
        )
        
        # Run transcription with VAD (voice activity detection)
        segments, info = self.model.transcribe(
            str(audio_file),
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        
        # Collect all segments
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)
        
        # Join all segments
        full_text = " ".join(text_parts).strip()
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Transcription completed",
            processing_time_ms=processing_time_ms,
            language_detected=info.language,
            language_probability=round(info.language_probability, 2)
        )
        
        return full_text, processing_time_ms


# Create a singleton instance
faster_whisper_stt = FasterWhisperSTT()
