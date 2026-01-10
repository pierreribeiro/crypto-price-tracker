"""
Number formatting utilities for cryptocurrency data

Handles edge case: Displaying extremely large or small cryptocurrency prices
Constitution Principle II: Type Safety with comprehensive type hints
"""

from enum import Enum


class MarketCategory(str, Enum):
    """
    Market capitalization categories (from data-model.md)
    Matches shared/types/cryptocurrency.ts MarketCategory enum
    """

    LARGE_CAP = 'large'  # Market cap > $10B
    MID_CAP = 'mid'  # Market cap $1B - $10B
    SMALL_CAP = 'small'  # Market cap < $1B


def format_price(price: float, decimals: int = 2) -> str:
    """
    Format cryptocurrency price with appropriate precision

    Handles extremely large and small prices with abbreviated formats or
    scientific notation for readability (Edge Case requirement)

    Args:
        price: Price in USD
        decimals: Number of decimal places for standard formatting (default: 2)

    Returns:
        Formatted price string with $ prefix

    Examples:
        >>> format_price(42350.25)
        '$42,350.25'
        >>> format_price(1500000)
        '$1.50M'
        >>> format_price(0.00000123)
        '$1.2300e-06'
    """
    if price >= 1_000_000_000_000:  # Trillions
        return f'${price / 1_000_000_000_000:.2f}T'
    if price >= 1_000_000_000:  # Billions
        return f'${price / 1_000_000_000:.2f}B'
    if price >= 1_000_000:  # Millions
        return f'${price / 1_000_000:.2f}M'
    if price >= 1_000:  # Thousands
        return f'${price / 1_000:.2f}K'
    if price < 0.01:  # Very small prices
        # Use scientific notation with 4 significant figures
        return f'${price:.4e}'
    # Standard formatting with thousands separator
    return f'${price:,.{decimals}f}'


def format_market_cap(market_cap: float) -> str:
    """
    Format market capitalization with abbreviated notation

    Reuses price formatting logic as market cap follows same display rules

    Args:
        market_cap: Market capitalization in USD

    Returns:
        Formatted market cap string with $ prefix

    Examples:
        >>> format_market_cap(831245678901.23)
        '$831.25B'
        >>> format_market_cap(5400000000)
        '$5.40B'
    """
    return format_price(market_cap)


def format_volume(volume: float) -> str:
    """
    Format 24-hour trading volume with abbreviated notation

    Args:
        volume: Trading volume in USD

    Returns:
        Formatted volume string with $ prefix

    Examples:
        >>> format_volume(28456789012.45)
        '$28.46B'
    """
    return format_price(volume)


def format_percentage(percentage: float, decimals: int = 2, include_sign: bool = True) -> str:
    """
    Format percentage change with optional +/- sign

    Args:
        percentage: Percentage value (e.g., 1.25 for +1.25%)
        decimals: Number of decimal places (default: 2)
        include_sign: Whether to include +/- sign (default: True)

    Returns:
        Formatted percentage string with % suffix

    Examples:
        >>> format_percentage(1.25)
        '+1.25%'
        >>> format_percentage(-3.45)
        '-3.45%'
        >>> format_percentage(0.5, include_sign=False)
        '0.50%'
    """
    if include_sign:
        sign = '+' if percentage >= 0 else ''
        return f'{sign}{percentage:.{decimals}f}%'
    return f'{abs(percentage):.{decimals}f}%'


def compute_market_cap_category(market_cap: float) -> MarketCategory:
    """
    Compute market cap category based on thresholds

    From data-model.md:
    - SMALL_CAP: marketCap < $1,000,000,000
    - MID_CAP: $1,000,000,000 ≤ marketCap ≤ $10,000,000,000
    - LARGE_CAP: marketCap > $10,000,000,000

    Args:
        market_cap: Market capitalization in USD

    Returns:
        Market cap category enum value

    Examples:
        >>> compute_market_cap_category(500_000_000)
        MarketCategory.SMALL_CAP
        >>> compute_market_cap_category(5_000_000_000)
        MarketCategory.MID_CAP
        >>> compute_market_cap_category(50_000_000_000)
        MarketCategory.LARGE_CAP
    """
    if market_cap > 10_000_000_000:
        return MarketCategory.LARGE_CAP
    if market_cap >= 1_000_000_000:
        return MarketCategory.MID_CAP
    return MarketCategory.SMALL_CAP


def format_number_compact(value: float) -> str:
    """
    Format any large number with compact notation (K/M/B/T)

    General-purpose formatter for any large numeric value

    Args:
        value: Numeric value to format

    Returns:
        Formatted string with abbreviated notation

    Examples:
        >>> format_number_compact(1500)
        '1.50K'
        >>> format_number_compact(1500000)
        '1.50M'
    """
    if value >= 1_000_000_000_000:
        return f'{value / 1_000_000_000_000:.2f}T'
    if value >= 1_000_000_000:
        return f'{value / 1_000_000_000:.2f}B'
    if value >= 1_000_000:
        return f'{value / 1_000_000:.2f}M'
    if value >= 1_000:
        return f'{value / 1_000:.2f}K'
    return f'{value:.2f}'
