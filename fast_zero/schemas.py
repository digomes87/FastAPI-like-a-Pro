from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Message(BaseModel):
    """Standard message response schema."""
    message: str = Field(description='Response message')


class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description='Username (3-50 chars, alphanumeric, underscore, hyphen only)'
    )
    email: EmailStr = Field(description='Valid email address')
    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description='User first name'
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description='User last name'
    )
    bio: Optional[str] = Field(
        default=None,
        max_length=500,
        description='User biography (max 500 chars)'
    )


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(
        min_length=8,
        max_length=255,
        description='Password (minimum 8 characters)'
    )


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$',
        description='Username (3-50 chars, alphanumeric, underscore, hyphen only)'
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description='Valid email address'
    )
    first_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description='User first name'
    )
    last_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description='User last name'
    )
    bio: Optional[str] = Field(
        default=None,
        max_length=500,
        description='User biography (max 500 chars)'
    )


class UserPublic(UserBase):
    """Public user schema (without sensitive information)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(description='Unique user identifier')
    is_active: bool = Field(description='Whether the user account is active')
    is_verified: bool = Field(description='Whether the user email is verified')
    created_at: datetime = Field(description='User creation timestamp')
    updated_at: datetime = Field(description='User last update timestamp')
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username


class UserInDB(UserBase):
    """User schema as stored in database (with sensitive information)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    password: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserList(BaseModel):
    """Schema for paginated user list response."""
    users: list[UserPublic] = Field(description='List of users')
    total: int = Field(default=0, description='Total number of users')
    page: int = Field(default=1, description='Current page number')
    per_page: int = Field(default=10, description='Items per page')
    pages: int = Field(default=1, description='Total number of pages')


# Legacy schemas for backward compatibility
UserSchema = UserCreate
UserDB = UserInDB
