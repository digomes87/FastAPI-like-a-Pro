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
        examples=[
            'postgresql://user:pass@localhost/db',
        ],
    )
    DATABASE_HOST: str = Field(
        default='localhost', description='Database host'
    )
    DATABASE_PORT: int = Field(default=5432, description='Database port')
    DATABASE_NAME: str = Field(
        default='fastapi_db', description='Database name'
    )
    DATABASE_USER: str = Field(
        default='fastapi_user', description='Database user'
    )
    DATABASE_PASSWORD: str = Field(
        default='fastapi_password', description='Database password'
    )

    # Application Configuration
    APP_NAME: str = Field(
        default='FastAPI Zero', description='Application name'
    )
    APP_VERSION: str = Field(
        default='0.1.0', description='Application version'
    )
    DEBUG: bool = Field(default=False, description='Debug mode')

    # Environment Configuration
    ENVIRONMENT: Literal['development', 'testing', 'production'] = Field(
        default='development', description='Application environment'
    )

    # Security Configuration
    SECRET_KEY: str = Field(
        default='your-secret-key-change-in-production',
        description='Secret key for JWT and other cryptographic operations',
        min_length=32,
    )
    ALGORITHM: str = Field(default='HS256', description='JWT algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description='Access token expiration time in minutes',
        ge=5,
        le=1440,  # Max 24 hours
    )

    # Password Security
    PASSWORD_MIN_LENGTH: int = Field(
        default=8, description='Minimum password length', ge=6, le=128
    )
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(
        default=True, description='Require uppercase letters in password'
    )
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(
        default=True, description='Require lowercase letters in password'
    )
    PASSWORD_REQUIRE_DIGITS: bool = Field(
        default=True, description='Require digits in password'
    )
    PASSWORD_REQUIRE_SPECIAL: bool = Field(
        default=True, description='Require special characters in password'
    )
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = Field(
        default=True,
        description='Require special characters in password (alias)',
    )

    # Rate Limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = Field(
        default=5,
        description='Maximum login attempts per IP per window',
        ge=1,
        le=100,
    )
    RATE_LIMIT_WINDOW_MINUTES: int = Field(
        default=15, description='Rate limit window in minutes', ge=1, le=60
    )
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description='Rate limit requests per window',
        ge=1,
        le=1000,
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=3600,
        description='Rate limit window in seconds',
        ge=60,
        le=86400,
    )

    # Account Security
    ACCOUNT_LOCKOUT_ATTEMPTS: int = Field(
        default=5,
        description='Maximum failed login attempts before account lockout',
        ge=3,
        le=20,
    )
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = Field(
        default=30,
        description='Account lockout duration in minutes',
        ge=5,
        le=1440,
    )
    MAX_LOGIN_ATTEMPTS: int = Field(
        default=5, description='Maximum login attempts (alias)', ge=3, le=20
    )
    LOCKOUT_DURATION: int = Field(
        default=900,
        description='Lockout duration in seconds',
        ge=300,
        le=86400,
    )

    # Google OAuth2 Configuration
    GOOGLE_CLIENT_ID: str = Field(
        default='', description='Google OAuth2 client ID'
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        default='', description='Google OAuth2 client secret'
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default='http://localhost:8000/auth/google/callback',
        description='Google OAuth2 redirect URI',
    )
    GOOGLE_DISCOVERY_URL: str = Field(
        default='https://accounts.google.com/.well-known/openid_configuration',
        description='Google OpenID Connect discovery URL',
    )

    # API Configuration
    API_V1_STR: str = Field(default='/api/v1', description='API v1 prefix')
    CORS_ORIGINS: str = Field(
        default='["http://localhost:3000","http://localhost:8000"]',
        description='CORS origins as JSON string',
    )

    # Testing Configuration
    TEST_DATABASE_URL: str = Field(
        default='postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db',
        description='Test database connection URL',
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
