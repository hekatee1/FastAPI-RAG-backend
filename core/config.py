# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    groq_api_key: str
    pinecone_api_key: str
    pinecone_index: str
    redis_url: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()