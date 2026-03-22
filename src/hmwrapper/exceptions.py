"""HMWrapper API exceptions."""


class HallmasterError(Exception):
    """Base exception for Hallmaster API errors."""


class AuthError(HallmasterError):
    """Authentication failed."""


class TokenError(HallmasterError):
    """Failed to extract anti-forgery token."""


class APIError(HallmasterError):
    """API request failed."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(APIError):
    """Rate limited by the Hallmaster server."""
