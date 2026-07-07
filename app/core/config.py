from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Conecta Volei Backend Lab"
    environment: str = "local"
    debug: bool = True
    database_url: str = (
        "postgresql+psycopg://username:password@localhost:5432/conecta_volei_lab"
    )
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    jwt_secret_key: str = "change-me-in-local-env"
    jwt_access_token_expire_minutes: int = 60 * 24
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()