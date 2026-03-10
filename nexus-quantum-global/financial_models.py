from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_STEALTH_URL: str = "https://api.vanguard-node.io/stealth"
    MAYA_RESONANCE_PHASE: int = 4
    HF_TOKEN: Optional[str] = None
    TARGET_PLATFORM: str = "https://target-tech-platform.com"

    REGION: str = "WEST"
    ENTORNO: str = "DEV"

    JWT_SECRET_KEY: str = "SOVEREIGN_MASTER_KEY_2026_ALPHA"

    AVATAR_ROOT_USER: Optional[str] = None
    AVATAR_ROOT_PASS: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()
