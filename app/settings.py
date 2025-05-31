from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        extra="ignore"
    )

    EXTRACTED_FILES_DIR: str = "extracted_files"

    API_KEY: str

@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings.

    :return: Settings instance with loaded environment variables.
    """
    return Settings()
