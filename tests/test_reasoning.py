import pytest
from unittest.mock import AsyncMock, MagicMock
from services.reasoning import ReasoningEngine
from schemas.persona import UserPersona

@pytest.fixture
def mock_vector_service():
    mock = AsyncMock()
    mock.search_by_vibe.return_value = [
        {"id": "1", "score": 0.9, "payload": {"name": "Test City"}}
    ]
    return mock

@pytest.fixture
def mock_llm_service():
    mock = AsyncMock()
    mock.generate_embedding.return_value = [0.1] * 384
    mock.generate_reasoning_chain.return_value = [{"step_id": 1, "logic": "test"}]
    return mock

@pytest.fixture
def mock_signal_service():
    mock = AsyncMock()
    mock.get_environmental_state.return_value = {"conditions": "Good"}
    mock.get_societal_state.return_value = {"crowd_density": 0.2}
    return mock

@pytest.mark.asyncio
async def test_generate_recommendation(mock_vector_service, mock_llm_service, mock_signal_service):
    engine = ReasoningEngine()
    engine.vector_store = mock_vector_service
    engine.llm = mock_llm_service
    engine.signals = mock_signal_service
    
    persona = UserPersona(
        preferences={"adventure": 0.8},
        constraints=["budget: Luxury"],
        mood="I want adventure"
    )
    
    result = await engine.generate_recommendation(persona)
    
    assert result["destination_name"] == "Test City"
    assert result["match_score"] == 0.9
    assert len(result["reasoning_chain"]) == 1
    mock_vector_service.search_by_vibe.assert_called_once()
