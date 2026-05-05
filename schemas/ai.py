from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    """
    Chat request for the travel assistant powered by Gemini 1.5 Pro/Flash.
    Includes session management and persona linkage as required by the
    epistemic foundations for contextual reasoning.
    """
    message: str = Field(
        ...,
        description="User's natural language message to the travel assistant"
    )
    persona_id: Optional[str] = Field(
        None,
        description="Link to the UserPersona for context-aware responses"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session ID for multi-turn conversation context management"
    )
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Previous messages in the session, e.g., [{'role': 'user', 'content': '...'}]"
    )


class AIChatResponse(BaseModel):
    """
    Chat response from the Gemini-powered travel assistant.
    Includes reasoning transparency and optional persona updates.
    """
    response: str = Field(
        ...,
        description="The assistant's natural language response"
    )
    reasoning: Optional[str] = Field(
        None,
        description="Reasoning chain explaining the assistant's logic"
    )
    session_id: str = Field(
        ...,
        description="Session ID for continuing the conversation"
    )
    persona_updates: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Any inferred updates to the UserPersona based on conversation, "
            "e.g., updated preference weights or new constraints"
        )
    )
