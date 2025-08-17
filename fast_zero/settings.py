from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings following 12-factor app principles."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='forbid',
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        description='Database connection URL',
        examples=['sqlite:///./database.db', 'postgresql://user:pass@localhost/db']
    )
    
    # Application Configuration
    APP_NAME: str = Field(default='FastAPI Zero', description='Application name')
    APP_VERSION: str = Field(default='0.1.0', description='Application version')
    DEBUG: bool = Field(default=False, description='Debug mode')
    
    # Environment Configuration
    ENVIRONMENT: Literal['development', 'testing', 'production'] = Field(
        default='development',
        description='Application environment'
    )
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default='your-secret-key-change-in-production',
        description='Secret key for JWT and other cryptographic operations'
    )
    ALGORITHM: str = Field(default='HS256', description='JWT algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description='Access token expiration time in minutes'
    )
    
    # API Configuration
    API_V1_STR: str = Field(default='/api/v1', description='API v1 prefix')
    
    # Testing Configuration
    TEST_DATABASE_URL: str = Field(
        default='sqlite:///./test_database.db',
        description='Test database connection URL'
    )
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == 'development'
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == 'testing'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == 'production'


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
