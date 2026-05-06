import uuid
import enum
from sqlalchemy import Column, String, Float, JSON, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from core.database import Base

class RegionType(str, enum.Enum):
    COASTAL = "Coastal"
    ALPINE = "Alpine"
    URBAN = "Urban"
    RURAL = "Rural"
    DESERT = "Desert"

class Destination(Base):
    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    
    # GeographicPoint primitives
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True) # in meters
    region_type = Column(Enum(RegionType), nullable=False)
    
    # Semantic/Dynamic state
    base_vibe = Column(JSON, nullable=False, default=list) # List of tags
    
    # EnvironmentState + SocialState (Dynamic ingestion)
    # Stored as JSON to handle high-velocity updates and signal complexity
    dynamic_state = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
