from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ConstraintType(str, Enum):
    """Constraint types as defined in ontology.md Section 4."""
    HARD = "hard"   # Boolean logic — if false, destination is pruned immediately
    SOFT = "soft"   # Weight-based — influences MatchScore but does not prune


class Constraint(BaseModel):
    """
    A single constraint object aligned with the ontology's Constraint Model.
    HardConstraints prune destinations; SoftConstraints influence scoring.
    """
    type: ConstraintType = Field(
        ...,
        description="'hard' = boolean prune if unmet, 'soft' = weight-based influence on MatchScore"
    )
    key: str = Field(
        ...,
        description="Constraint identifier, e.g., 'max_budget', 'wheelchair_access', 'dietary'"
    )
    value: str = Field(
        ...,
        description="Constraint value, e.g., '2000', 'true', 'vegetarian'"
    )
    weight: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Relevance weight for SoftConstraints (ignored for HardConstraints)"
    )


class UserPersonaBase(BaseModel):
    """
    The Personal Context (UserPersona) — aligned with ontology.md Section 2A.

    Represents the subjective state and requirements of the traveler with:
    - Preferences: Map of weights for preference-based ranking
    - Constraints: List of typed Constraint objects (Hard/Soft)
    - Mood: Semantic string vectorized via Text-Embedding-004 for Qdrant similarity search
    """
    preferences: Dict[str, float] = Field(
        default_factory=dict,
        description="Map of preference weights, e.g., {'adventure': 0.8, 'relaxation': 0.2}"
    )
    constraints: List[Constraint] = Field(
        default_factory=list,
        description="List of Constraint objects with type (hard/soft), key, value, and optional weight"
    )
    mood: Optional[str] = Field(
        None,
        description=(
            "Semantic mood string vectorized via Text-Embedding-004 "
            "and matched against destination BaseVibe in Qdrant. "
            "e.g., 'seeking solitude', 'vibrant energy'"
        )
    )


class UserPersonaCreate(UserPersonaBase):
    """Schema for creating a new UserPersona."""
    pass


class UserPersona(UserPersonaBase):
    """Full UserPersona with server-assigned ID."""
    id: str

    class Config:
        from_attributes = True
