from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    gcp_credentials_json: Optional[str] = None
    gcp_bucket_name: str
    gcp_project_id: Optional[str] = None

    baseten_api_key: str
    baseten_model_id: str

    class Config:
        env_file = Path(__file__).parent / ".env"
        case_sensitive = False

settings = Settings()