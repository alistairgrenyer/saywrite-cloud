from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "ok"


class TranscribeResponse(BaseModel):
    """Response model for transcription endpoint."""
    text: str


# Use a type alias instead of subclassing Dict so Pydantic v2 can generate a schema
Glossary = Dict[str, str]


class Profile(BaseModel):
    """User profile for rewrite requests."""
    id: str
    name: str
    tone: str
    constraints: List[str]
    format: Optional[str] = None
    audience: Optional[str] = None
    glossary: Optional[Glossary] = None
    max_words: Optional[int] = 350


class RewriteOptions(BaseModel):
    """Options for rewrite requests."""
    temperature: float = 0.5
    provider_hint: Optional[Literal["openai", "local"]] = None


class RewriteRequest(BaseModel):
    """Request model for rewrite endpoint."""
    transcript: str
    profile: Profile
    options: Optional[RewriteOptions] = Field(default_factory=RewriteOptions)


class UsageMetrics(BaseModel):
    """Usage metrics for API calls."""
    stt_ms: int = 0
    llm_ms: int = 0


class RewriteResponse(BaseModel):
    """Response model for rewrite endpoint."""
    draft: str
    usage: UsageMetrics


# Authentication schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class User(BaseModel):
    """User model."""
    id: str
    email: str
    is_active: bool = True
    created_at: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
