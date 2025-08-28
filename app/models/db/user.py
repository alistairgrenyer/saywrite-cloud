from sqlalchemy import Column, String, Boolean, UUID
import uuid

from app.core.database import BaseModel

class UserModel(BaseModel):
    """SQLAlchemy User model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    refresh_token = Column(String, nullable=True)
