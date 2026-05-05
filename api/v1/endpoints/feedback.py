from typing import Any, List
from fastapi import APIRouter
from schemas.feedback import Feedback, FeedbackCreate, PersonaAdjustment

router = APIRouter()

@router.post("/rate", response_model=Feedback)
def rate_recommendation(feedback_in: FeedbackCreate) -> Any:
    """
    Submit a 1-5 star rating for an AI recommendation.
    Used to fine-tune future Text-Embedding-004 vector searches in Qdrant.
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
    Gemini 1.5 Flash will process this to update the Persona preferences and constraints.
    """
    return {
        "status": "success",
        "message": f"Persona {adjustment.persona_id} updated based on correction.",
        "updates_made": [
            "preference 'museums' weight reduced: 0.7 → 0.1",
            "preference 'outdoor_markets' weight added: 0.8"
        ]
    }
