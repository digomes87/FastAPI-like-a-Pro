"""Google OAuth2 authentication module."""

from typing import Any, Dict

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, status

from fast_zero.settings import get_settings


class GoogleOAuth:
    """Google OAuth2 client for authentication."""

    def __init__(self):
        self.settings = get_settings()
        self.oauth = OAuth()

        # Register Google OAuth client
        self.oauth.register(
            name='google',
            client_id=self.settings.GOOGLE_CLIENT_ID,
            client_secret=self.settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url=self.settings.GOOGLE_DISCOVERY_URL,
            client_kwargs={'scope': 'openid email profile'},
        )

    def get_authorization_url(self, redirect_uri: str) -> str:
        """Get Google OAuth2 authorization URL.

        Args:
            redirect_uri: The redirect URI after authorization

        Returns:
            Authorization URL for Google OAuth2
        """
        # Build authorization URL manually
        auth_url = (
            f'https://accounts.google.com/o/oauth2/auth?'
            f'client_id={self.settings.GOOGLE_CLIENT_ID}&'
            f'redirect_uri={redirect_uri}&'
            f'scope=openid email profile&'
            f'response_type=code&'
            f'access_type=offline'
        )
        return auth_url

    async def get_user_info(
        self, code: str, redirect_uri: str
    ) -> Dict[str, Any]:
        """Exchange authorization code for user information.

        Args:
            code: Authorization code from Google
            redirect_uri: The redirect URI used in authorization

        Returns:
            User information from Google

        Raises:
            HTTPException: If token exchange or user info retrieval fails
        """
        try:
            # Exchange code for token
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    'https://oauth2.googleapis.com/token',
                    data={
                        'client_id': self.settings.GOOGLE_CLIENT_ID,
                        'client_secret': self.settings.GOOGLE_CLIENT_SECRET,
                        'code': code,
                        'grant_type': 'authorization_code',
                        'redirect_uri': redirect_uri,
                    },
                    headers={'Accept': 'application/json'},
                )

                if token_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            'Failed to exchange authorization code for token'
                        ),
                    )

                token_data = token_response.json()
                access_token = token_data.get('access_token')

                if not access_token:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='No access token received from Google',
                    )

                # Get user info
                user_response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'},
                )

                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Failed to get user information from Google',
                    )

                return user_response.json()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Network error during Google OAuth: {str(e)}',
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Unexpected error during Google OAuth: {str(e)}',
            )

    def validate_user_info(self, user_info: Dict[str, Any]) -> Dict[str, str]:
        """Validate and extract required user information.

        Args:
            user_info: Raw user information from Google

        Returns:
            Validated user information

        Raises:
            HTTPException: If required information is missing
        """
        required_fields = ['email', 'name', 'id']

        for field in required_fields:
            if field not in user_info:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Missing required field: {field}',
                )

        # Extract and validate email
        email = user_info.get('email', '').strip().lower()
        if not email or '@' not in email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid email address from Google',
            )

        # Extract name components
        full_name = user_info.get('name', '').strip()
        given_name = user_info.get('given_name', '').strip()
        family_name = user_info.get('family_name', '').strip()

        # Use given_name and family_name if available,
        # otherwise split full_name
        if given_name and family_name:
            first_name = given_name
            last_name = family_name
        elif full_name:
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        else:
            first_name = email.split('@')[0]  # Fallback to email username
            last_name = ''

        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'google_id': str(user_info['id']),
            'picture': user_info.get('picture', ''),
            'verified_email': user_info.get('verified_email', False),
        }


# Global instance
google_oauth = GoogleOAuth()
