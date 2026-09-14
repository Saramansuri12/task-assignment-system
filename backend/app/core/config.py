from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Intelligent Task Assignment System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"

    DATABASE_URL: str

    # Comma-separated list, overridable via CORS_ORIGINS in .env
    CORS_ORIGINS: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:4173,"
        "http://127.0.0.1:4173,"
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()