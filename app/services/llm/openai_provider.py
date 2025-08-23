import time
from typing import Optional

from openai import OpenAI, APIError

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import Profile, RewriteOptions

# Create logger
logger = get_logger(__name__)


class OpenAIProvider:
    """OpenAI provider for LLM services."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self._client = None
        self._model = settings.OPENAI_MODEL
        logger.info("Initializing OpenAI provider", model=self._model)
    
    @property
    def client(self) -> OpenAI:
        """
        Lazy-load the OpenAI client when first needed.
        
        Returns:
            OpenAI: The OpenAI client.
        """
        if self._client is None:
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set")
            
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        
        return self._client
    
    def _build_system_prompt(self, profile: Profile) -> str:
        """
        Build a system prompt from the user profile.
        
        Args:
            profile: User profile containing tone, constraints, etc.
            
        Returns:
            str: System prompt for the LLM.
        """
        # Start with basic instruction
        prompt = [
            f"You are an expert writer who rewrites text in the tone of {profile.name}.",
            f"Tone: {profile.tone}"
        ]
        
        # Add constraints
        if profile.constraints:
            prompt.append("Constraints:")
            for constraint in profile.constraints:
                prompt.append(f"- {constraint}")
        
        # Add format if specified
        if profile.format:
            prompt.append(f"Format: {profile.format}")
        
        # Add audience if specified
        if profile.audience:
            prompt.append(f"Target audience: {profile.audience}")
        
        # Add glossary if specified
        if profile.glossary:
            prompt.append("Glossary terms to include:")
            for term, definition in profile.glossary.items():
                prompt.append(f"- {term}: {definition}")
        
        # Add word limit if specified
        if profile.max_words:
            prompt.append(f"Keep the response under {profile.max_words} words.")
        
        return "\n".join(prompt)
    
    async def rewrite(
        self, 
        transcript: str, 
        profile: Profile, 
        options: Optional[RewriteOptions] = None
    ) -> tuple[str, int]:
        """
        Rewrite text using OpenAI.
        
        Args:
            transcript: Text to rewrite
            profile: User profile for rewriting
            options: Optional parameters for the request
            
        Returns:
            Tuple containing rewritten text and processing time in milliseconds
        """
        if options is None:
            options = RewriteOptions()
        
        start_time = time.time()
        
        system_prompt = self._build_system_prompt(profile)
        
        user_prompt = (
            f"Please rewrite the following transcript in the specified tone and style:\n\n"
            f"{transcript}"
        )
        
        try:
            logger.info(
                "Sending rewrite request to OpenAI",
                model=self._model,
                temperature=options.temperature,
                profile_id=profile.id,
                profile_name=profile.name,
            )
            
            response = self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=options.temperature,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            
            rewritten_text = response.choices[0].message.content.strip()
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "Rewrite completed",
                processing_time_ms=processing_time_ms,
                model=self._model,
                tokens_used=response.usage.total_tokens
            )
            
            return rewritten_text, processing_time_ms
            
        except APIError as e:
            logger.exception(
                "OpenAI API error",
                error=str(e),
                status_code=e.status_code if hasattr(e, 'status_code') else None
            )
            raise
        except Exception as e:
            logger.exception("Error in OpenAI rewrite", error=str(e))
            raise


# Create a singleton instance
openai_provider = OpenAIProvider()
