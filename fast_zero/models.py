from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    """User model representing application users."""
    
    __tablename__ = 'users'
    __table_args__ = {
        'comment': 'Application users table'
    }

    # Primary Key
    id: Mapped[int] = mapped_column(
        init=False,
        primary_key=True,
        comment='Unique user identifier'
    )
    
    # User Information
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment='Unique username for the user'
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        comment='User email address'
    )
    
    password: Mapped[Optional[str]] = mapped_column(
        String(255),
        default=None,
        comment='Hashed password (optional for OAuth users)'
    )
    
    # Optional fields
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        default=None,
        comment='User first name'
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        default=None,
        comment='User last name'
    )
    
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        default=None,
        comment='User biography'
    )
    
    # Status fields
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment='Whether the user account is active'
    )
    
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        comment='Whether the user email is verified'
    )
    
    # OAuth fields
    google_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        default=None,
        unique=True,
        index=True,
        comment='Google OAuth user ID'
    )
    
    picture: Mapped[Optional[str]] = mapped_column(
        String(500),
        default=None,
        comment='User profile picture URL'
    )
    
    oauth_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        default=None,
        comment='OAuth provider (google, etc.)'
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        comment='User creation timestamp'
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment='User last update timestamp'
    )
    
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f'<User(id={self.id}, username={self.username}, email={self.email})>'
    
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
