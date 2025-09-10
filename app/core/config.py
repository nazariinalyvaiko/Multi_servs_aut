"""Application configuration management using Pydantic settings."""

from typing import List, Optional
from pydantic import BaseSettings, Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_test_url: str = Field(..., env="DATABASE_TEST_URL")
    
    # JWT Configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis Configuration
    redis_url: str = Field(..., env="REDIS_URL")
    
    # Slack Configuration
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET")
    slack_app_token: str = Field(..., env="SLACK_APP_TOKEN")
    
    # Telegram Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: str = Field(..., env="TELEGRAM_WEBHOOK_URL")
    
    # Google Sheets Configuration
    google_credentials_file: str = Field(..., env="GOOGLE_CREDENTIALS_FILE")
    google_sheets_scopes: List[str] = Field(
        default=["https://www.googleapis.com/auth/spreadsheets"],
        env="GOOGLE_SHEETS_SCOPES"
    )
    
    # Application Configuration
    app_name: str = Field(default="Multi-Service Automation Platform", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
