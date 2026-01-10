"""
PriceDataPoint Pydantic model

Represents a single price observation at a specific timestamp
From data-model.md
Constitution Principle II: Type Safety
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PriceDataPoint(BaseModel):
    """
    Price observation at a specific timestamp

    Used for building historical trends and sparkline charts
    """

    timestamp: datetime = Field(
        ..., description='ISO 8601 timestamp of observation'
    )

    price: float = Field(
        ..., gt=0, description='Price in USD at this timestamp (must be positive)'
    )

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price is positive and finite"""
        if v <= 0:
            raise ValueError('Price must be positive')
        if not _is_finite(v):
            raise ValueError('Price must be finite')
        return v

    class Config:
        """Pydantic model configuration"""

        json_schema_extra = {
            'example': {
                'timestamp': '2026-01-09T12:00:00Z',
                'price': 42350.25,
            }
        }


def _is_finite(value: float) -> bool:
    """Check if a float value is finite (not NaN or infinity)"""
    import math

    return not (math.isnan(value) or math.isinf(value))
