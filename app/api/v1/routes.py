from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
import time
import tempfile
import os
from pathlib import Path

from app.models.schemas import (
    HealthResponse,
    TranscribeResponse,
    RewriteRequest,
    RewriteResponse,
    UsageMetrics,
    User
)
from app.core.logging import get_logger
from app.core.dependencies import get_current_active_user
from app.services.llm.factory import get_llm_provider
from app.services.stt.factory import get_stt_provider

# Create logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: A simple response indicating the service is running.
    """
    logger.info("Health check requested")
    return HealthResponse(status="ok")


@router.post("/transcribe", response_model=TranscribeResponse, tags=["transcribe"])
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user)
) -> TranscribeResponse:
    """
    Transcribe audio to text using OpenAI Whisper API.
    
    Args:
        audio: Audio file to transcribe
        language: Optional language hint
        
    Returns:
        TranscribeResponse: The transcribed text
    """
    logger.info("Transcribe request received", filename=audio.filename, language=language, user_id=current_user.id)
    
    # Validate audio file
    if not audio.filename:
        raise HTTPException(status_code=400, detail="Audio file is required")
    
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_file:
        temp_path = Path(temp_file.name)
        try:
            # Write audio data to temporary file
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Transcribe audio
            stt_provider = get_stt_provider()
            text, stt_ms = await stt_provider.transcribe(temp_path, language)
            
            return TranscribeResponse(text=text)
        
        except Exception as e:
            logger.exception("Error transcribing audio", error=str(e))
            raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")
        
        finally:
            # Clean up temporary file
            if temp_path.exists():
                os.unlink(temp_path)


@router.post("/rewrite", response_model=RewriteResponse, tags=["rewrite"])
async def rewrite_text(
    request: RewriteRequest,
    current_user: User = Depends(get_current_active_user)
) -> RewriteResponse:
    """
    Rewrite text using the configured LLM provider.
    
    Args:
        request: RewriteRequest containing transcript, profile, and options
        
    Returns:
        RewriteResponse: The rewritten text and usage metrics
    """
    start_time = time.time()
    
    logger.info(
        "Rewrite request received",
        profile_id=request.profile.id,
        profile_name=request.profile.name,
        transcript_length=len(request.transcript) if request.transcript else 0,
        user_id=current_user.id
    )
    
    # Validate request
    if not request.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    
    try:
        # Get LLM provider
        llm_provider = get_llm_provider()
        
        # Rewrite text
        rewritten_text, llm_ms = await llm_provider.rewrite(
            transcript=request.transcript,
            profile=request.profile,
            options=request.options
        )
        
        # Create usage metrics
        usage = UsageMetrics(
            stt_ms=0,  # No STT used in this endpoint
            llm_ms=llm_ms
        )
        
        return RewriteResponse(
            draft=rewritten_text,
            usage=usage
        )
        
    except ValueError as e:
        logger.exception("Value error in rewrite", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error in rewrite", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error rewriting text: {str(e)}")
