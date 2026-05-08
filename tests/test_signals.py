import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from services.signals import SignalService

@pytest.fixture
def signal_service():
    with patch('redis.asyncio.Redis') as mock_redis:
        mock_instance = mock_redis.return_value
        mock_instance.get = AsyncMock()
        mock_instance.set = AsyncMock()
        service = SignalService()
        return service, mock_instance

@pytest.mark.asyncio
async def test_get_environmental_state_cache_hit(signal_service):
    service, mock_redis = signal_service
    
    # Mock cache hit
    mock_redis.get.return_value = '{"temp": 20}'
    
    result = await service.get_environmental_state("dest1")
    
    assert result == {"temp": 20}
    mock_redis.get.assert_called_with("signal:env:dest1")

@pytest.mark.asyncio
async def test_get_environmental_state_cache_miss(signal_service):
    service, mock_redis = signal_service
    
    # Mock cache miss
    mock_redis.get.return_value = None
    
    result = await service.get_environmental_state("dest1")
    
    # It should return a default or fetch (currently it returns None if not in cache)
    # Wait, let's check the implementation.
    assert result is None
