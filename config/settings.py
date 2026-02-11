"""Configuration settings for Kingdom Wars Bot."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Bot configuration settings."""
    
    # Server settings
    port: int = 3000
    host: str = "0.0.0.0"
    
    # AWS Bedrock settings
    aws_region: str = "eu-north-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # AI Model settings
    primary_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    fallback_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # Bot metadata
    bot_name: str = "Mega ogudor"
    bot_strategy: str = "AI-trapped-strategy"
    bot_version: str = "1.0"
    
    # Performance settings
    request_timeout: float = 1.0
    ai_timeout: float = 0.8
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
