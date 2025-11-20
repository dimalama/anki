"""Application configuration"""

from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Anki Deck Generator"
    VERSION: str = "1.0.0"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Directory paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    CSV_DIR: Path = BASE_DIR / "csv"
    APKG_DIR: Path = BASE_DIR / "apkg"
    MEDIA_DIR: Path = BASE_DIR / "media"
    CONFIG_DIR: Path = BASE_DIR / "config"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # Ensure directories exist
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CSV_DIR.mkdir(exist_ok=True)
        self.APKG_DIR.mkdir(exist_ok=True)
        self.MEDIA_DIR.mkdir(exist_ok=True)
        self.CONFIG_DIR.mkdir(exist_ok=True)
        self.TEMPLATES_DIR.mkdir(exist_ok=True)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
