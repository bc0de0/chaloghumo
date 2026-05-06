import uuid
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    # UserPersona primitives
    preferences = Column(JSON, nullable=False, default=dict) # Weight map (e.g. adventure: 0.8)
    constraints = Column(JSON, nullable=False, default=list) # List of Hard/Soft constraints
    mood = Column(String, nullable=True) # Semantic string current state
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
