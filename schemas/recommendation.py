from typing import List, Dict, Any
from pydantic import BaseModel

class RecommendationBase(BaseModel):
    destination_id: str
    match_score: float
    reasoning_chain: List[str]
    context_snapshot: Dict[str, Any]

class RecommendationCreate(BaseModel):
    persona_id: str
    current_location: Optional[str] = None
    travel_dates: Dict[str, str]  # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}

class Recommendation(RecommendationBase):
    id: str
    
    class Config:
        from_attributes = True
