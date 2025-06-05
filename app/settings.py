from functools import lru_cache
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore"
    )

    EXTRACTED_FILES_DIR: str = "extracted_files"

    INFORMATION_EXTRACTION_MODEL: str = "gemini-2.0-flash"
    INFORMATION_EXTRACTION_PROMPT_FILE_PATH: str = "prompts/information_extraction.yaml"

    DB_AGENT_MODEL: str = "gemini-2.0-flash"
    DB_AGENT_PROMPT_FILE_PATH: str = "prompts/db_agent.yaml"
    INFORMATION_VALIDATION_AGENT_MODEL: str = "gemini-2.0-flash"
    INFORMATION_VALIDATION_AGENT_PROMPT_FILE_PATH: str = "prompts/information_validation_agent.yaml"
    SUPER_AGENT_MODEL: str = "gemini-2.0-flash"
    SUPER_AGENT_PROMPT_FILE_PATH: str = "prompts/super_agent.yaml"
    MAX_LOOPS: int = 3

    API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    FIREBASE_COLLECTION_NAME: str
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str

@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings.

    :return: Settings instance with loaded environment variables.
    """
    return Settings()

def load_env():
    settings = get_settings()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    os.environ["OPIK_API_KEY"] = settings.OPIK_API_KEY
    os.environ["OPIK_WORKSPACE"] = settings.OPIK_WORKSPACE
