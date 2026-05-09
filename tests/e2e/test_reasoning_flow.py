from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from schemas.persona import UserPersona
from services.external_apis.snowflake import snowflake_service
from services.external_apis.weather import weather_client
from services.postgres import postgres_service
from services.reasoning import TriageRouter, reasoning_engine


@pytest.mark.asyncio
async def test_triage_extraction_flow():
    """
    Test 1: User Input to JSON Extraction (Triage Stage).
    Ensures the 1.5B model correctly structured the user's intent.
    """
    router = TriageRouter()
    persona = UserPersona(
        mood="I want a quiet, snowy escape in the mountains with good coffee",
        preferences={"relaxation": 0.9, "nature": 0.8}
    )

    intent_plan = await router.analyze_intent(persona)

    assert "search_terms" in intent_plan
    assert len(intent_plan["search_terms"]) >= 1
    assert "signal_requirements" in intent_plan
    assert isinstance(intent_plan["signal_requirements"]["weather"], bool)


@pytest.mark.asyncio
async def test_reasoning_query_intelligence():
    """
    Test 2: Query Intelligence for all 4 Data Types.
    Focuses on LLM's ability to generate valid queries for heterogeneous sources.
    Mocks actual DB execution to isolate intelligence logic.
    """
    persona = UserPersona(
        mood="vibrant city with art and nightlife",
        preferences={"culture": 0.8, "nightlife": 0.7}
    )

    # Mocking data sources to focus on query generation & fusion
    with (
        patch(
            "services.postgres.postgres_service.fetch_candidate_ids",
            new_callable=AsyncMock,
        ) as mock_pg,
        patch(
            "services.vector_store.vector_service.search_by_vibe",
            new_callable=AsyncMock,
        ) as mock_qdrant,
        patch(
            "services.external_apis.snowflake.snowflake_service.validate_destination_trend",
            new_callable=AsyncMock,
        ) as mock_snowflake,
        patch(
            "services.signals.signal_service.get_environmental_state",
            new_callable=AsyncMock,
        ) as mock_weather,
        patch("services.signals.signal_service.redis") as mock_redis,
    ):
        
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        mock_pg.return_value = [1, 2, 3]
        mock_qdrant.return_value = [
            {"id": "1", "score": 0.9, "payload": {"name": "Paris"}}
        ]
        mock_snowflake.return_value = {"historical_score": 0.85, "is_trending": True}
        mock_weather.return_value = {"temp": 20, "condition": "Sunny"}

        recommendation = await reasoning_engine.generate_recommendation(persona)

        assert recommendation["destination_name"] != "Unknown"
        assert recommendation["match_score"] > 0
        assert len(recommendation["reasoning_chain"]) >= 1

        # Verify all intelligence layers were triggered
        mock_pg.assert_called()
        mock_qdrant.assert_called()
        mock_snowflake.assert_called()


@pytest.mark.asyncio
async def test_infrastructure_connectivity_check():
    """
    Test 3: Infrastructure Connectivity Health Check.
    Verifies if necessary connectors are initialized and ready for production logic.
    """
    # Check Snowflake
    assert hasattr(snowflake_service, "enabled")

    # Check Weather Client stubs as fallback
    weather_data = await weather_client.get_weather(0.0, 0.0)
    assert "temp" in weather_data

    # Check Postgres Service
    assert postgres_service is not None


@pytest.mark.asyncio
async def test_end_to_end_payload_consistency():
    """
    Test 4: Final Payload Consistency.
    Ensures the reasoning chain and context snapshot are correctly structured for the UI.
    """
    persona = UserPersona(
        mood="Beach vibe", 
        preferences={"sun": 0.9},
        travel_style="Luxury"
    )

    # We allow real LLM call here but mock slow DBs
    with (
        patch(
            "services.postgres.postgres_service.fetch_candidate_ids", return_value=[101]
        ),
        patch(
            "services.vector_store.vector_service.search_by_vibe",
            return_value=[
                {"id": "101", "score": 0.95, "payload": {"name": "Maldives"}}
            ],
        ),
        patch("services.signals.signal_service.redis") as mock_redis,
    ):
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        result = await reasoning_engine.generate_recommendation(persona)

        assert "context_snapshot" in result
        assert "persona" in result["context_snapshot"]
        assert "query_strategy" in result["context_snapshot"]
