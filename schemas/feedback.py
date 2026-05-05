from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class FeedbackBase(BaseModel):
    recommendation_id: str
    rating: int = Field(..., ge=1, le=5, description="1 to 5 star rating")
    comment: Optional[str] = None
    context_at_time: Dict[str, Any] = Field(default_factory=dict)

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class PersonaAdjustment(BaseModel):
    persona_id: str
    correction_text: str = Field(..., description="e.g., 'I actually hate museums'")
    automatic_update: bool = True
