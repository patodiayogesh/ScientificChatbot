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

    API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    FIREBASE_COLLECTION_NAME: str

@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings.

    :return: Settings instance with loaded environment variables.
    """
    return Settings()

def load_env():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_settings().GOOGLE_APPLICATION_CREDENTIALS
