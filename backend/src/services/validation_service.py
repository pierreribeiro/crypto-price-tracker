"""
Data validation service for cryptocurrency data

FR-018: Validate all external API data before display
Constitution Principle II: Type Safety
Based on data-model.md validation requirements
"""

from datetime import datetime, timezone
from typing import Any


class ValidationResult:
    """
    Result of cryptocurrency data validation

    Attributes:
        is_valid: Whether data passed all validation checks
        errors: List of validation error messages
        data: Validated data (only if is_valid is True)
    """

    def __init__(
        self, is_valid: bool, errors: list[str], data: Any = None
    ) -> None:
        self.is_valid = is_valid
        self.errors = errors
        self.data = data


def validate_cryptocurrency(data: dict[str, Any]) -> ValidationResult:
    """
    Validate cryptocurrency data from external APIs

    Implements validation rules from data-model.md to ensure data quality
    before display (FR-018)

    Args:
        data: Raw cryptocurrency data dictionary

    Returns:
        ValidationResult with validation status, errors, and cleaned data

    Validation Rules (from data-model.md):
        - currentPrice: Must be positive number
        - marketCap: Must be positive number
        - volume24h: Must be non-negative number (can be zero)
        - priceChangePercent24h: Must be finite number (can be negative)
        - rank: Must be 1-20 for top 20 display
        - lastUpdated: Must be valid date within last 5 minutes for cache validity
        - sparklineData: Must contain at least 1 point, maximum 168 points
    """
    errors: list[str] = []

    # Required string fields
    if not data.get('id') or not isinstance(data['id'], str):
        errors.append('Missing or invalid id: must be non-empty string')

    if not data.get('symbol') or not isinstance(data['symbol'], str):
        errors.append('Missing or invalid symbol: must be non-empty string')

    if not data.get('name') or not isinstance(data['name'], str):
        errors.append('Missing or invalid name: must be non-empty string')

    # Numeric validations
    current_price = data.get('currentPrice')
    if not isinstance(current_price, (int, float)) or current_price <= 0:
        errors.append('Invalid currentPrice: must be positive number')

    market_cap = data.get('marketCap')
    if not isinstance(market_cap, (int, float)) or market_cap <= 0:
        errors.append('Invalid marketCap: must be positive number')

    volume_24h = data.get('volume24h')
    if not isinstance(volume_24h, (int, float)) or volume_24h < 0:
        errors.append('Invalid volume24h: must be non-negative number')

    price_change_24h = data.get('priceChange24h')
    if not isinstance(price_change_24h, (int, float)):
        errors.append('Invalid priceChange24h: must be number')

    # Percentage validation (must be finite, can be negative)
    price_change_percent = data.get('priceChangePercent24h')
    if (
        not isinstance(price_change_percent, (int, float))
        or not _is_finite(price_change_percent)
    ):
        errors.append(
            'Invalid priceChangePercent24h: must be finite number'
        )

    # Rank validation (1-20 for top 20 cryptocurrencies)
    rank = data.get('rank')
    if not isinstance(rank, int) or rank < 1 or rank > 20:
        errors.append('Invalid rank: must be integer between 1 and 20')

    # Date validation
    last_updated = data.get('lastUpdated')
    if not isinstance(last_updated, datetime):
        errors.append('Invalid lastUpdated: must be datetime object')
    else:
        # Check if data is fresh (within 5 minutes for cache validity)
        age_minutes = (
            datetime.now(timezone.utc) - last_updated
        ).total_seconds() / 60
        if age_minutes > 5:
            errors.append(
                f'Invalid lastUpdated: data is stale ({age_minutes:.1f} minutes old, '
                'must be within 5 minutes)'
            )

    # Sparkline validation
    sparkline_data = data.get('sparklineData')
    if not isinstance(sparkline_data, list):
        errors.append('Invalid sparklineData: must be array')
    elif len(sparkline_data) > 168:
        errors.append(
            'Invalid sparklineData: maximum 168 data points allowed '
            '(7 days * 24 hours)'
        )
    elif len(sparkline_data) > 0:
        # Validate sparkline data points
        for i, point in enumerate(sparkline_data):
            if not isinstance(point, dict):
                errors.append(
                    f'Invalid sparklineData[{i}]: must be PriceDataPoint object'
                )
                continue

            if not isinstance(point.get('timestamp'), datetime):
                errors.append(
                    f'Invalid sparklineData[{i}].timestamp: must be datetime'
                )

            price = point.get('price')
            if not isinstance(price, (int, float)) or price <= 0:
                errors.append(
                    f'Invalid sparklineData[{i}].price: must be positive number'
                )

    # Price direction validation
    price_direction = data.get('priceDirection')
    if price_direction not in ['up', 'down']:
        errors.append("Invalid priceDirection: must be 'up' or 'down'")

    # Market cap category validation
    market_cap_category = data.get('marketCapCategory')
    if market_cap_category not in ['small', 'mid', 'large']:
        errors.append(
            "Invalid marketCapCategory: must be 'small', 'mid', or 'large'"
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        data=data if len(errors) == 0 else None,
    )


def validate_price_data_point(point: dict[str, Any]) -> ValidationResult:
    """
    Validate a single price data point for sparkline

    Args:
        point: Price data point dictionary with timestamp and price

    Returns:
        ValidationResult with validation status and errors
    """
    errors: list[str] = []

    # Timestamp validation
    if not isinstance(point.get('timestamp'), datetime):
        errors.append('Invalid timestamp: must be datetime object')

    # Price validation
    price = point.get('price')
    if not isinstance(price, (int, float)) or price <= 0:
        errors.append('Invalid price: must be positive number')

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        data=point if len(errors) == 0 else None,
    )


def _is_finite(value: float) -> bool:
    """
    Check if a float value is finite (not NaN or infinity)

    Args:
        value: Float value to check

    Returns:
        True if value is finite, False otherwise
    """
    import math

    return not (math.isnan(value) or math.isinf(value))


def filter_valid_cryptocurrencies(
    crypto_list: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Filter cryptocurrency list, separating valid from invalid entries

    Implements edge case handling: API responses contain malformed data
    Logs errors for debugging while ensuring app doesn't crash (per requirement)

    Args:
        crypto_list: List of cryptocurrency data dictionaries

    Returns:
        Tuple of (valid_cryptos, invalid_cryptos_with_errors)

    Example:
        ```python
        valid, invalid = filter_valid_cryptocurrencies(api_response)
        if invalid:
            print(f"Filtered {len(invalid)} invalid entries")
        return valid
        ```
    """
    valid_cryptos: list[dict[str, Any]] = []
    invalid_cryptos: list[dict[str, Any]] = []

    for crypto_data in crypto_list:
        validation = validate_cryptocurrency(crypto_data)

        if validation.is_valid and validation.data:
            valid_cryptos.append(validation.data)
        else:
            # Store invalid crypto with error details for logging
            invalid_cryptos.append(
                {
                    'id': crypto_data.get('id', 'unknown'),
                    'errors': validation.errors,
                    'data': crypto_data,
                }
            )

    # Log aggregate errors for monitoring
    if invalid_cryptos:
        print(
            f'⚠️  Filtered {len(invalid_cryptos)} invalid cryptocurrencies '
            f'from API response'
        )
        for invalid in invalid_cryptos:
            print(f"  - {invalid['id']}: {invalid['errors']}")

    return (valid_cryptos, invalid_cryptos)
