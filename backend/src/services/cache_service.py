"""
Redis caching service with TTL support

FR-016: 5-minute caching for price data
Constitution Principle III: API Reliability
Based on data-model.md caching strategy
"""

import json
import os
from typing import Any, Optional

from redis.asyncio import Redis

from src.lib.redis_client import get_redis_client


class CacheService:
    """
    Service for caching cryptocurrency data in Redis

    Implements cache key structure from data-model.md:
    - crypto:list:top20 → List of top 20 cryptocurrencies (TTL: 5 minutes)
    - crypto:details:{id} → Individual cryptocurrency details (TTL: 5 minutes)
    - crypto:gainers:top20 → Top 20 gainers list (TTL: 5 minutes)
    - crypto:losers:top20 → Top 20 losers list (TTL: 5 minutes)
    - crypto:sparkline:{id} → 7-day sparkline data (TTL: 1 hour)
    """

    def __init__(self) -> None:
        """Initialize cache service"""
        # Default TTL values from data-model.md
        self.default_ttl = int(
            os.getenv('CACHE_TTL_SECONDS', '300')
        )  # 5 minutes
        self.sparkline_ttl = 3600  # 1 hour (sparkline is less volatile)

    def _get_client(self) -> Redis:
        """Get Redis client instance"""
        return get_redis_client()

    async def get_top_cryptocurrencies(
        self, include_sparkline: bool = True
    ) -> Optional[list[dict[str, Any]]]:
        """
        Get cached top 20 cryptocurrencies

        Args:
            include_sparkline: Whether sparkline data is included

        Returns:
            List of cryptocurrency dictionaries, or None if cache miss
        """
        key = 'crypto:list:top20'
        return await self._get_json(key)

    async def set_top_cryptocurrencies(
        self,
        data: list[dict[str, Any]],
        ttl: Optional[int] = None,
        include_sparkline: bool = True,
    ) -> None:
        """
        Cache top 20 cryptocurrencies

        Args:
            data: List of cryptocurrency dictionaries
            ttl: Time-to-live in seconds (default: 5 minutes)
            include_sparkline: Whether sparkline data is included
        """
        key = 'crypto:list:top20'
        await self._set_json(key, data, ttl or self.default_ttl)

    async def get_gainers(self) -> Optional[list[dict[str, Any]]]:
        """Get cached top 20 gainers"""
        key = 'crypto:gainers:top20'
        return await self._get_json(key)

    async def set_gainers(
        self, data: list[dict[str, Any]], ttl: Optional[int] = None
    ) -> None:
        """Cache top 20 gainers"""
        key = 'crypto:gainers:top20'
        await self._set_json(key, data, ttl or self.default_ttl)

    async def get_losers(self) -> Optional[list[dict[str, Any]]]:
        """Get cached top 20 losers"""
        key = 'crypto:losers:top20'
        return await self._get_json(key)

    async def set_losers(
        self, data: list[dict[str, Any]], ttl: Optional[int] = None
    ) -> None:
        """Cache top 20 losers"""
        key = 'crypto:losers:top20'
        await self._set_json(key, data, ttl or self.default_ttl)

    async def get_cryptocurrency_details(
        self, crypto_id: str
    ) -> Optional[dict[str, Any]]:
        """
        Get cached cryptocurrency details

        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')

        Returns:
            Cryptocurrency dictionary, or None if cache miss
        """
        key = f'crypto:details:{crypto_id}'
        return await self._get_json(key)

    async def set_cryptocurrency_details(
        self,
        crypto_id: str,
        data: dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """
        Cache cryptocurrency details

        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')
            data: Cryptocurrency dictionary
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        key = f'crypto:details:{crypto_id}'
        await self._set_json(key, data, ttl or self.default_ttl)

    async def get_sparkline(
        self, crypto_id: str
    ) -> Optional[list[dict[str, Any]]]:
        """
        Get cached sparkline data

        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')

        Returns:
            List of PriceDataPoint dictionaries, or None if cache miss
        """
        key = f'crypto:sparkline:{crypto_id}'
        return await self._get_json(key)

    async def set_sparkline(
        self,
        crypto_id: str,
        data: list[dict[str, Any]],
        ttl: Optional[int] = None,
    ) -> None:
        """
        Cache sparkline data

        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')
            data: List of PriceDataPoint dictionaries
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        key = f'crypto:sparkline:{crypto_id}'
        await self._set_json(key, data, ttl or self.sparkline_ttl)

    async def _get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON data from cache

        Args:
            key: Cache key

        Returns:
            Deserialized JSON data, or None if cache miss
        """
        try:
            client = self._get_client()
            value = await client.get(key)

            if value is None:
                return None

            # Deserialize JSON with datetime handling
            return json.loads(value)

        except Exception as e:
            print(f'⚠️  Cache get error for key {key}: {e}')
            return None

    async def _set_json(
        self, key: str, data: Any, ttl: int
    ) -> None:
        """
        Set JSON data in cache with TTL

        Args:
            key: Cache key
            data: Data to serialize and cache
            ttl: Time-to-live in seconds
        """
        try:
            client = self._get_client()

            # Serialize to JSON with datetime handling
            value = json.dumps(data, default=_json_serializer)

            await client.setex(key, ttl, value)

        except Exception as e:
            print(f'⚠️  Cache set error for key {key}: {e}')
            # Don't raise - cache failures shouldn't break the app

    async def delete(self, key: str) -> None:
        """
        Delete a cache entry

        Args:
            key: Cache key to delete
        """
        try:
            client = self._get_client()
            await client.delete(key)
        except Exception as e:
            print(f'⚠️  Cache delete error for key {key}: {e}')

    async def clear_all(self) -> None:
        """
        Clear all cryptocurrency cache entries

        Useful for testing or manual cache invalidation
        """
        try:
            client = self._get_client()
            # Delete all keys matching crypto:* pattern
            async for key in client.scan_iter(match='crypto:*'):
                await client.delete(key)
            print('✅ Cache cleared successfully')
        except Exception as e:
            print(f'⚠️  Cache clear error: {e}')


def _json_serializer(obj: Any) -> Any:
    """
    Custom JSON serializer for datetime and other special types

    Args:
        obj: Object to serialize

    Returns:
        Serializable representation

    Raises:
        TypeError: If object type is not serializable
    """
    from datetime import datetime

    if isinstance(obj, datetime):
        return obj.isoformat()

    raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
