from typing import Optional, List
from pydantic import BaseModel

class AIChatRequest(BaseModel):
    message: str
    context_id: Optional[str] = None
    stream: bool = False

class AIChatResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None

class PackingListRequest(BaseModel):
    destination_id: str
    days: int
    activity_types: List[str]

class PackingListResponse(BaseModel):
    items: List[str]
    category_breakdown: dict
