from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    status: str = Field(..., example="online")
    version: str = Field(..., example="0.1.0")
    services: dict[str, str] = Field(
        ...,
        example={
            "database": "connected",
            "qdrant": "connected",
            "redis": "connected",
            "llm": "available",
        },
    )
