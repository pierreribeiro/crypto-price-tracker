"""
Error handling utilities for CryptoTracker Pro

Constitution Principle VI: Error Resilience
Provides standardized error handling and user-friendly error messages (FR-019)
"""

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """
    Standard error response model (matches api-specification.yaml)

    Constitution Principle II: Type Safety
    """

    message: str
    code: Optional[str] = None
    timestamp: str
    details: Optional[dict[str, Any]] = None


class APIError(HTTPException):
    """
    Base exception class for API errors

    Extends FastAPI's HTTPException with standardized error format
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize API error

        Args:
            status_code: HTTP status code
            message: Human-readable error message (FR-019)
            code: Machine-readable error code
            details: Additional error context
        """
        self.error_detail = ErrorDetail(
            message=message,
            code=code,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details,
        )

        super().__init__(
            status_code=status_code,
            detail=self.error_detail.model_dump(exclude_none=True),
        )


class ExternalAPIError(APIError):
    """
    Raised when external API calls fail

    Used when both CoinGecko and CoinMarketCap APIs are unavailable
    """

    def __init__(
        self,
        message: str = 'External API unavailable. Please try again later.',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code='EXTERNAL_API_FAILURE',
            details=details,
        )


class CacheError(APIError):
    """
    Raised when cache operations fail

    Usually indicates Redis connectivity issues
    """

    def __init__(
        self,
        message: str = 'Cache service temporarily unavailable.',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            code='CACHE_ERROR',
            details=details,
        )


class ValidationError(APIError):
    """
    Raised when request validation fails

    Used for invalid query parameters or request body
    """

    def __init__(
        self,
        message: str = 'Invalid request parameters.',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            code='VALIDATION_ERROR',
            details=details,
        )


class NotFoundError(APIError):
    """
    Raised when requested resource is not found

    Used for cryptocurrency not found, no search results, etc.
    """

    def __init__(
        self,
        message: str = 'Resource not found.',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code='NOT_FOUND',
            details=details,
        )


class RateLimitError(APIError):
    """
    Raised when rate limit is exceeded

    Used when external API rate limits are hit
    """

    def __init__(
        self,
        message: str = 'Rate limit exceeded. Please try again later.',
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            code='RATE_LIMIT_EXCEEDED',
            details=details,
        )


def format_validation_errors(errors: list[str]) -> ErrorDetail:
    """
    Format validation errors into standardized error response

    Args:
        errors: List of validation error messages

    Returns:
        ErrorDetail with formatted validation errors
    """
    return ErrorDetail(
        message='Data validation failed',
        code='VALIDATION_ERROR',
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={'errors': errors},
    )


def create_degraded_service_warning() -> str:
    """
    Create warning message for degraded service (503 responses)

    Used when serving stale cached data due to API failures

    Returns:
        Warning message string
    """
    return 'Data may be stale. External APIs unavailable.'


def safe_error_message(exception: Exception) -> str:
    """
    Convert exception to user-friendly error message

    Sanitizes technical error details to prevent information leakage
    while maintaining useful context for users (FR-019)

    Args:
        exception: The exception to convert

    Returns:
        User-friendly error message
    """
    # Known error types with friendly messages
    error_mappings = {
        'TimeoutError': 'Request timed out. Please try again.',
        'ConnectionError': 'Unable to connect to service. Please try again later.',
        'HTTPStatusError': 'External service error. Please try again later.',
        'ValidationError': 'Invalid data format. Please check your input.',
    }

    exception_type = type(exception).__name__

    # Return mapped message or generic fallback
    return error_mappings.get(
        exception_type, 'An unexpected error occurred. Please try again later.'
    )
