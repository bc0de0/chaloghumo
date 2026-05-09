"""
Configuration Module for ChaloGhumo.

This module centralizes all environment-specific settings using Pydantic's 
BaseSettings. It handles validation and normalization of credentials for 
databases, external APIs, and cloud services.
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Global Application Settings.
    
    Automatically loaded from environment variables or a .env file.
    Includes configuration for PostgreSQL, Qdrant, Redis, Kafka, and multiple 
    External API providers.
    """
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ChaloGhumo"
    VERSION: str = "0.1.0"

    # --- CORS Configuration ---
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Parses and validates CORS origin lists."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # --- Relational Database (PostgreSQL) ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "chaloghumo"

    # --- Vector Database (Qdrant) ---
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # --- Memory & Cache (Redis) ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # --- Event Stream (Kafka) ---
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # --- Intelligence (Together AI) ---
    TOGETHER_API_KEY: str = ""

    # --- Real-Time Signal APIs ---
    OPENWEATHER_API_KEY: str = ""
    AMADEUS_API_KEY: str = ""
    TICKETMASTER_API_KEY: str = ""
    PREDICTHQ_API_KEY: str = ""
    GDELT_API_KEY: str = ""

    # --- Cloud Storage (AWS S3 Landing Zone) ---
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "chaloghumo-etl-raw-prod"

    # --- Analytical Memory (Snowflake) ---
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_SCHEMA: str = ""
    SNOWFLAKE_WAREHOUSE: str = ""

    class Config:
        """Pydantic configuration for the Settings class."""
        case_sensitive = True
        env_file = ".env"


# Global singleton instance for use throughout the application
settings = Settings()
