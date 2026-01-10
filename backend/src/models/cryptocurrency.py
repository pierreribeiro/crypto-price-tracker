"""
Cryptocurrency Pydantic model

Core entity for cryptocurrency data
From data-model.md
Constitution Principle II: Type Safety
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.models.market_category import MarketCategory
from src.models.price_data_point import PriceDataPoint


class Cryptocurrency(BaseModel):
    """
    Represents a digital currency with all attributes for display and filtering

    Implements validation rules from data-model.md
    """

    # Identification
    id: str = Field(
        ..., min_length=1, description='Unique identifier from API (e.g., "bitcoin")'
    )

    symbol: str = Field(
        ..., min_length=1, description='Trading symbol (e.g., "BTC")'
    )

    name: str = Field(
        ..., min_length=1, description='Full name (e.g., "Bitcoin")'
    )

    # Current Market Data
    currentPrice: float = Field(
        ...,
        gt=0,
        description='Current price in USD (FR-002) - must be positive',
        alias='current_price',
    )

    marketCap: float = Field(
        ...,
        gt=0,
        description='Market capitalization in USD (FR-005) - must be positive',
        alias='market_cap',
    )

    volume24h: float = Field(
        ...,
        ge=0,
        description='24-hour trading volume in USD (FR-005) - must be non-negative',
        alias='volume_24h',
    )

    # Price Changes
    priceChange24h: float = Field(
        ...,
        description='Absolute price change in 24h (FR-003)',
        alias='price_change_24h',
    )

    priceChangePercent24h: float = Field(
        ...,
        description='Percentage price change in 24h (FR-003) - must be finite',
        alias='price_change_percent_24h',
    )

    # Trend Data
    sparklineData: list[PriceDataPoint] = Field(
        default_factory=list,
        max_length=168,
        description='7-day price history for sparkline chart (FR-011)',
        alias='sparkline_data',
    )

    # Metadata
    rank: int = Field(
        ...,
        ge=1,
        le=20,
        description='Market cap ranking (FR-001: top 20) - must be 1-20',
    )

    lastUpdated: datetime = Field(
        ...,
        description='Timestamp of last data update (FR-015)',
        alias='last_updated',
    )

    # Computed Properties
    priceDirection: Literal['up', 'down'] = Field(
        ...,
        description='Derived from priceChangePercent24h (FR-004)',
        alias='price_direction',
    )

    marketCapCategory: MarketCategory = Field(
        ...,
        description='Derived from marketCap thresholds (FR-010)',
        alias='market_cap_category',
    )

    @field_validator('priceChangePercent24h')
    @classmethod
    def validate_price_change_percent(cls, v: float) -> float:
        """Validate price change percentage is finite"""
        if not _is_finite(v):
            raise ValueError('priceChangePercent24h must be finite number')
        return v

    @field_validator('sparklineData')
    @classmethod
    def validate_sparkline_data(
        cls, v: list[PriceDataPoint]
    ) -> list[PriceDataPoint]:
        """Validate sparkline data has at most 168 points (7 days * 24 hours)"""
        if len(v) > 168:
            raise ValueError(
                'sparklineData must have maximum 168 data points (7 days hourly)'
            )
        return v

    class Config:
        """Pydantic model configuration"""

        populate_by_name = True  # Allow both camelCase and snake_case
        json_schema_extra = {
            'example': {
                'id': 'bitcoin',
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'current_price': 42350.25,
                'market_cap': 831245678901.23,
                'volume_24h': 28456789012.45,
                'price_change_24h': 523.75,
                'price_change_percent_24h': 1.25,
                'sparkline_data': [
                    {'timestamp': '2026-01-09T12:00:00Z', 'price': 42350.25}
                ],
                'rank': 1,
                'last_updated': '2026-01-09T12:30:00Z',
                'price_direction': 'up',
                'market_cap_category': 'large',
            }
        }


def _is_finite(value: float) -> bool:
    """Check if a float value is finite (not NaN or infinity)"""
    import math

    return not (math.isnan(value) or math.isinf(value))
