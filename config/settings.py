from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = ""
    erp_connector: str = "mock"
    mock_db_path: str = "data/mock_erp.db"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.2

    match_score_threshold: float = 65.0
    assessment_score_threshold: float = 75.0
    interview_slots_count: int = 12


@lru_cache
def get_settings() -> Settings:
    return Settings()