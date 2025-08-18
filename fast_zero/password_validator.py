"""Password validation utilities for enhanced security."""

import re
from typing import List

from fast_zero.settings import get_settings

settings = get_settings()


class PasswordValidationError(Exception):
    """Exception raised when password validation fails."""

    def __init__(self, message: str, errors: List[str]):
        self.message = message
        self.errors = errors
        super().__init__(self.message)


class PasswordValidator:
    """Password validator with configurable security rules."""

    def __init__(self):
        self.min_length = settings.PASSWORD_MIN_LENGTH
        self.require_uppercase = settings.PASSWORD_REQUIRE_UPPERCASE
        self.require_lowercase = settings.PASSWORD_REQUIRE_LOWERCASE
        self.require_digits = settings.PASSWORD_REQUIRE_DIGITS
        self.require_special = settings.PASSWORD_REQUIRE_SPECIAL

        # Common weak passwords to reject
        self.weak_passwords = {
            'password',
            '123456',
            '123456789',
            'qwerty',
            'abc123',
            'password123',
            'admin',
            'letmein',
            'welcome',
            'monkey',
            '1234567890',
            'password1',
            '123123',
            'admin123',
        }

    def validate(self, password: str) -> None:
        """Validate password against security rules.

        Args:
            password: Password to validate

        Raises:
            PasswordValidationError: If password doesn't meet requirements
        """
        errors = []

        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                f'Password must be at least {self.min_length} characters long'
            )

        # Check maximum length (prevent DoS)
        if len(password) > 128:
            errors.append('Password must be no more than 128 characters long')

        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append(
                'Password must contain at least one uppercase letter'
            )

        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append(
                'Password must contain at least one lowercase letter'
            )

        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append('Password must contain at least one digit')

        # Check for special characters
        if self.require_special and not re.search(
            r'[!@#$%^&*(),.?":{}|<>\-_]', password
        ):
            errors.append(
                'Password must contain at least one special character '
                '(!@#$%^&*(),.?":{}|<>-_)'
            )

        # Check against common weak passwords
        if password.lower() in self.weak_passwords:
            errors.append('Password is too common and easily guessable')

        # Check for repeated characters (more than 3 in a row)
        if re.search(r'(.)\1{3,}', password):
            errors.append(
                'Password cannot contain more than 3 repeated '
                'characters in a row'
            )

        # Check for sequential characters
        if self._has_sequential_chars(password):
            errors.append(
                'Password cannot contain sequential characters '
                '(e.g., 123, abc)'
            )

        if errors:
            raise PasswordValidationError(
                'Password does not meet security requirements', errors
            )

    def _has_sequential_chars(self, password: str) -> bool:
        """Check if password contains sequential characters.

        Args:
            password: Password to check

        Returns:
            True if sequential characters found, False otherwise
        """
        password_lower = password.lower()

        # Check for sequential numbers
        for i in range(len(password_lower) - 2):
            if password_lower[i : i + 3].isdigit():
                nums = [int(c) for c in password_lower[i : i + 3]]
                if nums[1] == nums[0] + 1 and nums[2] == nums[1] + 1:
                    return True

        # Check for sequential letters
        for i in range(len(password_lower) - 2):
            if password_lower[i : i + 3].isalpha():
                chars = password_lower[i : i + 3]
                if (
                    ord(chars[1]) == ord(chars[0]) + 1
                    and ord(chars[2]) == ord(chars[1]) + 1
                ):
                    return True

        return False

    def get_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100).

        Args:
            password: Password to evaluate

        Returns:
            Strength score from 0 (weakest) to 100 (strongest)
        """
        score = 0

        # Length score (up to 25 points)
        if len(password) >= 8:
            score += min(25, len(password) * 2)

        # Character variety (up to 40 points)
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10

        # Complexity bonus (up to 35 points)
        unique_chars = len(set(password))
        score += min(15, unique_chars)

        # No repeated patterns
        if not re.search(r'(.)\1{2,}', password):
            score += 10

        # No sequential characters
        if not self._has_sequential_chars(password):
            score += 10

        return min(100, score)


# Global password validator instance
password_validator = PasswordValidator()
