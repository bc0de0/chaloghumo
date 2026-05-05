from typing import Any, List
from fastapi import APIRouter, HTTPException
from schemas.persona import UserPersona, UserPersonaCreate

router = APIRouter()

# Mock storage for initial setup
db_personas = []

@router.post("/", response_model=UserPersona)
def create_persona(persona_in: UserPersonaCreate) -> Any:
    """
    Create a new travel persona.
    """
    new_persona = {
        **persona_in.model_dump(),
        "id": f"p-{len(db_personas) + 1}"
    }
    db_personas.append(new_persona)
    return new_persona

@router.get("/", response_model=List[UserPersona])
def read_personas() -> Any:
    """
    Retrieve all user personas.
    """
    return db_personas

@router.get("/{persona_id}", response_model=UserPersona)
def read_persona(persona_id: str) -> Any:
    """
    Get a specific persona by ID.
    """
    persona = next((p for p in db_personas if p["id"] == persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona
