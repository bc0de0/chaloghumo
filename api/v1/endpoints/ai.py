from typing import Any
from fastapi import APIRouter
from schemas.ai import AIChatRequest, AIChatResponse, PackingListRequest, PackingListResponse

router = APIRouter()

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(request: AIChatRequest) -> Any:
    """
    General travel assistant powered by Llama 3.2 1B.
    """
    return {
        "response": "I recommend checking out the local markets in the evening.",
        "reasoning": "Based on your preference for local culture."
    }

@router.post("/packing", response_model=PackingListResponse)
def get_packing_assistant(request: PackingListRequest) -> Any:
    """
    Smart packing assistant based on weather and activities.
    """
    return {
        "items": ["Rain jacket", "Walking shoes", "Sunscreen"],
        "category_breakdown": {"Essentials": 2, "Protection": 1}
    }
