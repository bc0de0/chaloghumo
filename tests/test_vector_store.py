import pytest
from unittest.mock import MagicMock, patch
from services.vector_store import VectorService
from qdrant_client.http import models

@pytest.fixture
def vector_service():
    with patch('services.vector_store.QdrantClient') as mock_qdrant:
        service = VectorService()
        return service, mock_qdrant.return_value

@pytest.mark.asyncio
async def test_upsert_destination(vector_service):
    service, mock_client = vector_service
    
    # Mock return values for collection existence check
    mock_client.get_collections.return_value = MagicMock(collections=[])
    
    payload = {
        "name": "Paris",
        "country": "FR",
        "lat": 48.8,
        "lng": 2.3,
        "vibe_description": "Test vibe",
        "budget_level": "Luxury",
        "climate_type": "Temperate",
        "safety_index": 0.9,
        "tags": ["history"]
    }
    
    success = await service.upsert_destination("id1", [0.1]*384, payload)
    
    assert success is True
    mock_client.upsert.assert_called_once()
    mock_client.create_collection.assert_called_once()

@pytest.mark.asyncio
async def test_search_by_vibe(vector_service):
    service, mock_client = vector_service
    
    # Mock search results
    mock_hit = MagicMock()
    mock_hit.id = "id1"
    mock_hit.score = 0.99
    mock_hit.payload = {"name": "Paris"}
    mock_client.search.return_value = [mock_hit]
    mock_client.get_collections.return_value = MagicMock(collections=[MagicMock(name="destinations")])
    
    results = await service.search_by_vibe([0.1]*384)
    
    assert len(results) == 1
    assert results[0]["id"] == "id1"
    assert results[0]["payload"]["name"] == "Paris"
