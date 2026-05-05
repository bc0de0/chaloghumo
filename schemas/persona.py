from typing import List, Optional
from pydantic import BaseModel, Field

class UserPersonaBase(BaseModel):
    name: str
    budget_level: str = Field(..., description="Low, Medium, High, or Luxury")
    interests: List[str] = Field(default_factory=list, description="e.g., Hiking, Museums, Nightlife")
    dietary_preferences: List[str] = Field(default_factory=list)
    accessibility_requirements: Optional[str] = None
    travel_pace: str = Field("Moderate", description="Relaxed, Moderate, or Fast-paced")

class UserPersonaCreate(UserPersonaBase):
    pass

class UserPersona(UserPersonaBase):
    id: str

    class Config:
        from_attributes = True
