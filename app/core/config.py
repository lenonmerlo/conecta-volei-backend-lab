from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Conecta Volei Backend Lab"
    environment: str = "local"
    debug: bool = True
    database_url: str = (
        "postgresql+psycopg://username:password@localhost:5432/conecta_volei_lab"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()