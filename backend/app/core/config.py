from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "QuantLab Backend"
    database_url: str = "postgresql+psycopg2://quantlab:quantlab@db:5432/quantlab"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
