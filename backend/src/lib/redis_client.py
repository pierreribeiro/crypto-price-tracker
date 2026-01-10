"""
Redis connection pool with async support

Constitution Principle III: API Reliability
Provides connection pooling for efficient Redis operations
"""

import os
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool


# Global connection pool instance
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


def get_redis_url() -> str:
    """
    Construct Redis connection URL from environment variables

    Returns:
        Redis connection URL (redis://host:port/db)
    """
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', '6379'))
    db = int(os.getenv('REDIS_DB', '0'))
    password = os.getenv('REDIS_PASSWORD', '')

    if password:
        return f'redis://:{password}@{host}:{port}/{db}'
    return f'redis://{host}:{port}/{db}'


async def init_redis_pool() -> None:
    """
    Initialize Redis connection pool

    Should be called during application startup
    Creates a connection pool with optimized settings for async operations
    """
    global _redis_pool, _redis_client

    redis_url = get_redis_url()

    # Create connection pool with async support
    _redis_pool = ConnectionPool.from_url(
        redis_url,
        max_connections=10,  # Maximum concurrent connections
        decode_responses=True,  # Automatically decode responses to strings
        socket_connect_timeout=5,  # Connection timeout in seconds
        socket_keepalive=True,  # Enable TCP keepalive
        retry_on_timeout=True,  # Retry operations on timeout
    )

    # Create Redis client from pool
    _redis_client = Redis(connection_pool=_redis_pool)

    # Verify connection
    await _redis_client.ping()
    print('✅ Redis connection pool initialized successfully')


async def close_redis_pool() -> None:
    """
    Close Redis connection pool

    Should be called during application shutdown
    Ensures all connections are properly closed
    """
    global _redis_pool, _redis_client

    if _redis_client:
        await _redis_client.close()
        _redis_client = None

    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None

    print('✅ Redis connection pool closed successfully')


def get_redis_client() -> Redis:
    """
    Get Redis client instance

    Returns:
        Redis client with async support

    Raises:
        RuntimeError: If connection pool not initialized
    """
    if _redis_client is None:
        raise RuntimeError(
            'Redis connection pool not initialized. '
            'Call init_redis_pool() during application startup.'
        )

    return _redis_client


async def ping_redis() -> tuple[bool, Optional[float]]:
    """
    Ping Redis server to check connectivity and measure latency

    Returns:
        Tuple of (connected: bool, latency_ms: float or None)
    """
    try:
        client = get_redis_client()

        # Measure latency
        import time

        start = time.time()
        await client.ping()
        latency_ms = (time.time() - start) * 1000

        return (True, latency_ms)

    except Exception as e:
        print(f'❌ Redis ping failed: {e}')
        return (False, None)
