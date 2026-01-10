"""
Health check endpoint

Constitution Principle III: API Reliability
From contracts/api-specification.yaml
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from src.lib.redis_client import ping_redis
from src.services.coingecko_client import CoinGeckoClient
from src.services.coinmarketcap_client import CoinMarketCapClient


router = APIRouter()


@router.get('/health')
async def health_check() -> dict[str, any]:
    """
    Health check endpoint

    Returns API health status and dependency connectivity:
    - Overall status (healthy or degraded)
    - Cache (Redis) connectivity and latency
    - External API (CoinGecko, CoinMarketCap) availability

    Implements endpoint from api-specification.yaml

    Returns:
        Health status response with system status and dependency checks
    """
    # Check Redis connectivity
    redis_connected, redis_latency = await ping_redis()

    # Check external API availability
    coingecko_client = CoinGeckoClient()
    coinmarketcap_client = CoinMarketCapClient()

    coingecko_available = await coingecko_client.ping()
    coinmarketcap_available = await coinmarketcap_client.ping()

    # Determine overall health status
    # System is degraded if Redis is down OR both external APIs are down
    status = 'healthy'
    if not redis_connected:
        status = 'degraded'
    elif not coingecko_available and not coinmarketcap_available:
        status = 'degraded'

    return {
        'status': status,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'cache': {
            'connected': redis_connected,
            'latency_ms': redis_latency if redis_latency else None,
        },
        'external_apis': {
            'coingecko': (
                'available' if coingecko_available else 'unavailable'
            ),
            'coinmarketcap': (
                'available' if coinmarketcap_available else 'unavailable'
            ),
        },
    }
