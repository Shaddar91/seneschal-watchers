from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://seneschal:seneschal@localhost:5433/seneschal_db"
    poll_interval_seconds: int = 3600
    ai_api_url: str = "http://localhost:11434"
    ai_model: str = "llama3"
    log_level: str = "INFO"

    model_config = {"env_prefix": "SENESCHAL_WATCHERS_"}


settings = Settings()
