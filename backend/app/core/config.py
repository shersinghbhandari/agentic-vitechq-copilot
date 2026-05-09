from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VitechQ"
    RAW_UPLOAD_DIR: str = "data/raw"
    VIRUS_SCAN_ENABLED: bool = False
    MAX_UPLOAD_SIZE_MB: int = "5"
    ENABLE_VIRUS_SCAN: bool = "false"

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()