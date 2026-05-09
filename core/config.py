from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ChaloGhumo"
    VERSION: str = "0.1.0"

    # CORS
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "chaloghumo"

    # Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # AI
    TOGETHER_API_KEY: str = ""

    # External APIs
    OPENWEATHER_API_KEY: str = ""
    AMADEUS_API_KEY: str = ""
    TICKETMASTER_API_KEY: str = ""
    PREDICTHQ_API_KEY: str = ""
    GDELT_API_KEY: str = ""

    # AWS (S3 Landing Zone)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "chaloghumo-etl-raw-prod"

    # Snowflake
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_SCHEMA: str = ""
    SNOWFLAKE_WAREHOUSE: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
