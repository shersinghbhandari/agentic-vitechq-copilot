from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VitechQ"

    # Virus related setting
    VIRUS_SCAN_ENABLED: bool = False
    ENABLE_VIRUS_SCAN: bool = "false"

    # File related setting
    RAW_UPLOAD_DIR: str = "data/raw"

    RAW_STAGING_TEMP_DIR: str = "data/stage"
    RAW_STAGING_QUARANTINE_DIR: str = "data/stage/quarantine"
    RAW_STAGING_APPROVED_DIR: str = "data/stage/approved"

    MAX_UPLOAD_SIZE_MB: int = "5"

    VECTOR_STORE_PROVIDER: str = "pgvector"
    EMBEDDING_DIMENSIONS: int = 384

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