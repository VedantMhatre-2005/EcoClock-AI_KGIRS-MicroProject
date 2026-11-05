import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "EcoClock AI"
    API_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    TESTING: bool = False

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR.as_posix()}/data/ecoclock.db"

    # Neo4j
    NEO4J_ENABLED: bool = True
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "ecoclock_secure_pass_2026"
    NEO4J_READONLY_USERNAME: str = "neo4j_readonly"
    NEO4J_READONLY_PASSWORD: str = "ecoclock_ro_pass_2026"

    # Ollama LLM
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_TIMEOUT: int = 60
    LLM_EXTRACTION_ENABLED: bool = False  # Set to True only if manual slow LLM re-extraction is desired

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Climate Clock Defaults
    CLIMATE_TARGET_DATE: str = "2040-12-31"
    BASELINE_YEAR: int = 2024
    INSTITUTION_NAME: str = "VESIT Green Campus"

    # Synthetic Data
    SYNTHETIC_DATA_SEED: int = 42
    USE_SYNTHETIC_DATA: bool = True

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
