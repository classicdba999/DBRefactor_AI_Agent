"""
Configuration management for DBRefactor AI Agent.

Uses pydantic-settings for environment variable management.
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DatabaseConfig(BaseSettings):
    """Database connection configuration"""

    # Source Database (Oracle)
    source_db_host: str = Field(default="localhost")
    source_db_port: int = Field(default=1521)
    source_db_name: str = Field(default="ORCL")
    source_db_user: str = Field(default="")
    source_db_password: str = Field(default="")

    # Target Database (PostgreSQL)
    target_db_host: str = Field(default="localhost")
    target_db_port: int = Field(default=5432)
    target_db_name: str = Field(default="postgres")
    target_db_user: str = Field(default="")
    target_db_password: str = Field(default="")

    # Application Database (MySQL)
    app_db_host: str = Field(default="localhost")
    app_db_port: int = Field(default=3306)
    app_db_name: str = Field(default="migration_tracker")
    app_db_user: str = Field(default="")
    app_db_password: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


class AIConfig(BaseSettings):
    """AI/LLM configuration"""

    # Google Gemini
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-pro")

    # OpenAI (optional)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4-turbo-preview")

    # Anthropic Claude (optional)
    anthropic_api_key: Optional[str] = Field(default=None)
    anthropic_model: str = Field(default="claude-3-sonnet-20240229")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


class RedisConfig(BaseSettings):
    """Redis configuration for caching and task queue"""

    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


class AppConfig(BaseSettings):
    """Application configuration"""

    # Application
    app_name: str = Field(default="DBRefactor AI Agent")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Security
    secret_key: str = Field(default="change-this-in-production")
    cors_origins: List[str] = Field(default=["*"])

    # Agent Configuration
    max_agent_retries: int = Field(default=3)
    agent_timeout_seconds: int = Field(default=300)

    # Workflow Configuration
    max_workflow_steps: int = Field(default=100)
    workflow_step_timeout_seconds: int = Field(default=600)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


class Settings:
    """Combined settings"""

    def __init__(self):
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.ai = AIConfig()
        self.redis = RedisConfig()


# Global settings instance
settings = Settings()
