from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Invoice Agent"
    environment: str = "development"

    ollama_base_url: str = "https://ollama.com"
    ollama_chat_model: str = "gpt-oss:20b"
    ollama_embedding_model: str = "embeddinggemma"

    chroma_db_path: Path = BASE_DIR / "chroma_db"
    policy_path: Path = BASE_DIR / "knowledge" / "invoice_policy.txt"
    collection_name : str =  "invoice_policies"

    langsmith_tracing: bool = False
    langsmith_project: str = "ai-invoice-agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    max_tool_rounds: int = 5
    approval_threshold: int = 200_000


@lru_cache
def get_settings() -> Settings:
    return Settings()