"""
Retry logic with exponential backoff for external API calls

Constitution Principle III: API Reliability
Handles transient failures gracefully with configurable retry strategies
"""

import asyncio
import functools
from typing import Any, Callable, Optional, TypeVar, cast

import httpx


# Type variable for generic function signatures
T = TypeVar('T')


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted"""

    def __init__(self, attempts: int, last_exception: Exception) -> None:
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(
            f'Retry exhausted after {attempts} attempts. '
            f'Last error: {type(last_exception).__name__}: {last_exception}'
        )


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an exception is retryable

    Args:
        exception: The exception to check

    Returns:
        True if the error is transient and should be retried
    """
    # HTTP timeout errors are retryable
    if isinstance(exception, (httpx.TimeoutException, asyncio.TimeoutError)):
        return True

    # HTTP connection errors are retryable
    if isinstance(exception, (httpx.ConnectError, httpx.ConnectTimeout)):
        return True

    # HTTP 5xx server errors are retryable (temporary server issues)
    if isinstance(exception, httpx.HTTPStatusError):
        return 500 <= exception.response.status_code < 600

    # HTTP 429 (rate limit) is retryable with backoff
    if isinstance(exception, httpx.HTTPStatusError):
        return exception.response.status_code == 429

    # Other errors are not retryable
    return False


async def exponential_backoff_delay(attempt: int, base_delay: float = 1.0) -> None:
    """
    Sleep with exponential backoff

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds (default: 1.0)

    Delays:
        - Attempt 0: 1 second
        - Attempt 1: 2 seconds
        - Attempt 2: 4 seconds
        - Attempt 3: 8 seconds
        - Maximum: 30 seconds
    """
    delay = min(base_delay * (2**attempt), 30.0)
    await asyncio.sleep(delay)


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying async functions with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        retryable_exceptions: Tuple of exception types to retry (default: all Exception)

    Returns:
        Decorated function with retry logic

    Example:
        ```python
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        async def fetch_api_data():
            async with httpx.AsyncClient() as client:
                response = await client.get('https://api.example.com/data')
                response.raise_for_status()
                return response.json()
        ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None

            for attempt in range(max_attempts):
                try:
                    # Execute the function
                    result = await func(*args, **kwargs)
                    return cast(T, result)

                except retryable_exceptions as e:
                    last_exception = e

                    # Check if this specific error is retryable
                    if not is_retryable_error(e):
                        # Non-retryable error, raise immediately
                        raise

                    # Log retry attempt
                    print(
                        f'⚠️  Retry attempt {attempt + 1}/{max_attempts} '
                        f'for {func.__name__}: {type(e).__name__}: {e}'
                    )

                    # If this was the last attempt, raise RetryExhausted
                    if attempt == max_attempts - 1:
                        raise RetryExhausted(max_attempts, e) from e

                    # Wait with exponential backoff before next attempt
                    await exponential_backoff_delay(attempt, base_delay)

            # This should never be reached, but type checker needs it
            assert last_exception is not None
            raise RetryExhausted(max_attempts, last_exception)

        return cast(Callable[..., T], wrapper)

    return decorator


# Convenience decorator with default settings for API calls
retry_api_call = retry_with_backoff(
    max_attempts=3,
    base_delay=1.0,
    retryable_exceptions=(
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.HTTPStatusError,
    ),
)
