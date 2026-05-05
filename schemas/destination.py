from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DestinationBase(BaseModel):
    name: str
    country: str
    category: str
    description: str
    tags: List[str]
    base_cost_index: float  # 0.0 to 1.0

class DestinationCreate(DestinationBase):
    pass

class Destination(DestinationBase):
    id: str
    coordinates: Dict[str, float]  # {"lat": 0.0, "lng": 0.0}
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True
