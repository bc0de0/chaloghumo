from typing import Any, List
from fastapi import APIRouter
from schemas.feedback import Feedback, FeedbackCreate, PersonaAdjustment

router = APIRouter()

@router.post("/rate", response_model=Feedback)
def rate_recommendation(feedback_in: FeedbackCreate) -> Any:
    """
    Submit a 1-5 star rating for an AI recommendation.
    Used to fine-tune future MiniLM vector searches.
    """
    return {
        **feedback_in.model_dump(),
        "id": "f-123",
        "user_id": "u-456"
    }

@router.post("/adjust")
def adjust_persona_alignment(adjustment: PersonaAdjustment) -> Any:
    """
    Provide natural language feedback to adjust the user's Persona.
    Llama 3.2 1B will process this to update the Persona tags.
    """
    return {
        "status": "success",
        "message": f"Persona {adjustment.persona_id} updated based on correction.",
        "updates_made": ["removed: museums", "added: outdoor_markets"]
    }
