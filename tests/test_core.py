import pytest
from core.config import settings

def test_settings_initialization():
    assert settings.PROJECT_NAME == "ChaloGhumo"
    assert settings.API_V1_STR == "/api/v1"
    # Ensure database settings are present
    assert hasattr(settings, "POSTGRES_SERVER")
    assert hasattr(settings, "REDIS_HOST")
    assert hasattr(settings, "QDRANT_HOST")

def test_cors_origins_validator():
    # Test validator with string
    from core.config import Settings
    s = Settings(BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000")
    assert len(s.BACKEND_CORS_ORIGINS) == 2
    assert str(s.BACKEND_CORS_ORIGINS[0]) == "http://localhost:3000/"
