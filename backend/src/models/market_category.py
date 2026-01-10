"""
MarketCategory enum

Classification of cryptocurrencies based on market capitalization
From data-model.md
Constitution Principle II: Type Safety
"""

from enum import Enum


class MarketCategory(str, Enum):
    """
    Market capitalization categories for filtering

    Thresholds (from data-model.md):
    - SMALL_CAP: marketCap < $1,000,000,000
    - MID_CAP: $1,000,000,000 ≤ marketCap ≤ $10,000,000,000
    - LARGE_CAP: marketCap > $10,000,000,000
    """

    LARGE_CAP = 'large'  # Market cap > $10B
    MID_CAP = 'mid'  # Market cap $1B - $10B
    SMALL_CAP = 'small'  # Market cap < $1B
