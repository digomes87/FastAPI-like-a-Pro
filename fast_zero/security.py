"""Security utilities for authentication and rate limiting."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.async_services import get_async_user_service
from fast_zero.settings import get_settings

settings = get_settings()


class RateLimiter:
    """In-memory rate limiter for login attempts."""
    
    def __init__(self):
        self._attempts: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited.
        
        Args:
            identifier: IP address or user identifier
            
        Returns:
            True if rate limited, False otherwise
        """
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=settings.RATE_LIMIT_WINDOW_MINUTES)
            
            # Clean old attempts
            self._attempts[identifier] = [
                attempt_time for attempt_time in self._attempts[identifier]
                if attempt_time > window_start
            ]
            
            # Check if rate limited
            return len(self._attempts[identifier]) >= settings.RATE_LIMIT_LOGIN_ATTEMPTS
    
    async def record_attempt(self, identifier: str) -> None:
        """Record a login attempt.
        
        Args:
            identifier: IP address or user identifier
        """
        async with self._lock:
            self._attempts[identifier].append(datetime.now())
    
    async def clear_attempts(self, identifier: str) -> None:
        """Clear attempts for identifier (on successful login).
        
        Args:
            identifier: IP address or user identifier
        """
        async with self._lock:
            if identifier in self._attempts:
                del self._attempts[identifier]


class AccountLockout:
    """Account lockout management."""
    
    def __init__(self):
        self._failed_attempts: Dict[str, int] = defaultdict(int)
        self._lockout_times: Dict[str, datetime] = {}
        self._lock = asyncio.Lock()
    
    async def is_locked_out(self, username: str) -> bool:
        """Check if account is locked out.
        
        Args:
            username: Username to check
            
        Returns:
            True if locked out, False otherwise
        """
        async with self._lock:
            if username not in self._lockout_times:
                return False
            
            lockout_time = self._lockout_times[username]
            lockout_duration = timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES)
            
            if datetime.now() > lockout_time + lockout_duration:
                # Lockout expired, clear it
                del self._lockout_times[username]
                self._failed_attempts[username] = 0
                return False
            
            return True
    
    async def record_failed_attempt(self, username: str) -> None:
        """Record a failed login attempt.
        
        Args:
            username: Username that failed login
        """
        async with self._lock:
            self._failed_attempts[username] += 1
            
            if self._failed_attempts[username] >= settings.ACCOUNT_LOCKOUT_ATTEMPTS:
                self._lockout_times[username] = datetime.now()
    
    async def clear_failed_attempts(self, username: str) -> None:
        """Clear failed attempts for username (on successful login).
        
        Args:
            username: Username to clear
        """
        async with self._lock:
            self._failed_attempts[username] = 0
            if username in self._lockout_times:
                del self._lockout_times[username]
    
    async def get_lockout_info(self, username: str) -> Optional[Dict[str, any]]:
        """Get lockout information for username.
        
        Args:
            username: Username to check
            
        Returns:
            Lockout info dict or None if not locked out
        """
        async with self._lock:
            if username not in self._lockout_times:
                return None
            
            lockout_time = self._lockout_times[username]
            lockout_duration = timedelta(minutes=settings.ACCOUNT_LOCKOUT_DURATION_MINUTES)
            unlock_time = lockout_time + lockout_duration
            
            if datetime.now() > unlock_time:
                return None
            
            return {
                'locked_at': lockout_time,
                'unlock_at': unlock_time,
                'remaining_minutes': int((unlock_time - datetime.now()).total_seconds() / 60)
            }


class SecurityManager:
    """Centralized security management."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.account_lockout = AccountLockout()
    
    async def check_login_security(self, request: Request, username: str) -> None:
        """Check all security constraints before login attempt.
        
        Args:
            request: FastAPI request object
            username: Username attempting login
            
        Raises:
            HTTPException: If security constraints are violated
        """
        client_ip = self._get_client_ip(request)
        
        # Check rate limiting by IP
        if await self.rate_limiter.is_rate_limited(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f'Too many login attempts. Try again in {settings.RATE_LIMIT_WINDOW_MINUTES} minutes.',
                headers={'Retry-After': str(settings.RATE_LIMIT_WINDOW_MINUTES * 60)}
            )
        
        # Check account lockout
        if await self.account_lockout.is_locked_out(username):
            lockout_info = await self.account_lockout.get_lockout_info(username)
            if lockout_info:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f'Account is locked. Try again in {lockout_info["remaining_minutes"]} minutes.',
                    headers={'Retry-After': str(lockout_info['remaining_minutes'] * 60)}
                )
    
    async def record_login_attempt(self, request: Request, username: str, success: bool) -> None:
        """Record login attempt and update security state.
        
        Args:
            request: FastAPI request object
            username: Username that attempted login
            success: Whether login was successful
        """
        client_ip = self._get_client_ip(request)
        
        if success:
            # Clear security state on successful login
            await self.rate_limiter.clear_attempts(client_ip)
            await self.account_lockout.clear_failed_attempts(username)
        else:
            # Record failed attempt
            await self.rate_limiter.record_attempt(client_ip)
            await self.account_lockout.record_failed_attempt(username)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else '127.0.0.1'


class UserSecurityService:
    """User-specific security operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_service = get_async_user_service(session)
    
    async def check_user_security_status(self, username: str) -> Dict[str, any]:
        """Check user security status.
        
        Args:
            username: Username to check
            
        Returns:
            Security status information
        """
        user = await self.user_service.get_user_by_username(username)
        if not user:
            return {'exists': False}
        
        return {
            'exists': True,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
    
    async def validate_user_for_login(self, username: str) -> None:
        """Validate user can attempt login.
        
        Args:
            username: Username to validate
            
        Raises:
            HTTPException: If user cannot login
        """
        user = await self.user_service.get_user_by_username(username)
        
        if not user:
            # Don't reveal if user exists or not
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Account is deactivated'
            )


# Global security manager instance
security_manager = SecurityManager()