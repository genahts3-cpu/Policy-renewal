from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = "sk-_58eVef-ywwIJ1ApjsxRlA"
    openai_base_url: str = "https://genailab.tcs.in/v1"
    openai_model: str = "genailab-maas-gpt-4o"
    embedding_model: str = "azure/genailab-maas-text-embedding-3-large"

    secret_key: str = "policy-renewal-agent-secret-key-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    database_url: str = "sqlite:///./data/policy_renewal.db"
    chroma_persist_dir: str = "./data/chroma"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "policy-renewal-agent"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
