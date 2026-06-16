"""UCSK Configuration — centralised environment settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    # General
    app_name: str = "UCSK"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Qdrant (Vector DB)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "ucsk_fingerprints"
    qdrant_embedding_dim: int = 1024

    # Neo4j (Graph DB)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ucsk_secret"

    # PostgreSQL (Event Store)
    postgres_dsn: str = "postgresql+asyncpg://ucsk:ucsk@localhost:5432/ucsk"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Sensing thresholds
    focus_threshold: float = 0.7
    fatigue_threshold: float = 0.4
    frustration_threshold: float = 0.6

    # WebRTC / P2P
    webrtc_signaling_url: str = "ws://localhost:9000/signaling"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_prefix": "UCSK_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
