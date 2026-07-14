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
    cors_allowed_origins: str = (
        "http://localhost:5173,http://localhost:5174"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()