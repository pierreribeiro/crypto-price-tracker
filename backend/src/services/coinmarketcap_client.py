"""
CoinMarketCap API client as fallback data source

Fallback data source when CoinGecko is unavailable (FR-022)
Constitution Principle III: API Reliability with retry logic
"""

import os
from datetime import datetime
from typing import Any

import httpx

from src.lib.retry import retry_api_call


class CoinMarketCapClient:
    """
    Client for CoinMarketCap API

    Used as fallback when CoinGecko API is unavailable
    Note: Free tier doesn't provide sparkline data
    """

    def __init__(self) -> None:
        """Initialize CoinMarketCap client with API key"""
        self.api_key = os.getenv('COINMARKETCAP_API_KEY', '')
        if not self.api_key:
            print(
                '⚠️  Warning: COINMARKETCAP_API_KEY not set. '
                'Fallback API will not work.'
            )

        self.base_url = 'https://pro-api.coinmarketcap.com/v1'
        self.headers = {
            'Accept': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    @retry_api_call
    async def get_top_cryptocurrencies(
        self, limit: int = 20, include_sparkline: bool = True
    ) -> list[dict[str, Any]]:
        """
        Fetch top cryptocurrencies by market cap

        Note: include_sparkline parameter is ignored as CoinMarketCap free tier
        doesn't provide sparkline data

        Args:
            limit: Number of cryptocurrencies to fetch (default: 20)
            include_sparkline: Ignored (CoinMarketCap limitation)

        Returns:
            List of cryptocurrency data dictionaries

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.TimeoutException: On request timeout
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f'{self.base_url}/cryptocurrency/listings/latest',
                params={
                    'start': 1,
                    'limit': limit,
                    'convert': 'USD',
                    'sort': 'market_cap',
                    'sort_dir': 'desc',
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()['data']

    @retry_api_call
    async def ping(self) -> bool:
        """
        Ping CoinMarketCap API to check availability

        Returns:
            True if API is available, False otherwise
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0)
            ) as client:
                response = await client.get(
                    f'{self.base_url}/key/info', headers=self.headers
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f'⚠️  CoinMarketCap API ping failed: {e}')
            return False


def map_coinmarketcap_response(api_data: dict[str, Any]) -> dict[str, Any]:
    """
    Map CoinMarketCap API response to internal Cryptocurrency model

    From data-model.md mapping specification

    Note: CoinMarketCap free tier doesn't provide sparkline data,
    so sparklineData will be empty array

    Args:
        api_data: Raw CoinMarketCap API response data

    Returns:
        Mapped cryptocurrency data matching internal model
    """
    from src.lib.formatters import compute_market_cap_category

    usd_quote = api_data['quote']['USD']

    # Compute absolute price change from percentage
    price_change_24h = (
        usd_quote['percent_change_24h'] / 100
    ) * usd_quote['price']

    return {
        'id': api_data['symbol'].lower(),  # Use symbol as ID
        'symbol': api_data['symbol'],
        'name': api_data['name'],
        'currentPrice': usd_quote['price'],
        'marketCap': usd_quote['market_cap'],
        'volume24h': usd_quote['volume_24h'],
        'priceChange24h': price_change_24h,
        'priceChangePercent24h': usd_quote['percent_change_24h'],
        'sparklineData': [],  # CoinMarketCap free tier limitation
        'rank': api_data['cmc_rank'],
        'lastUpdated': datetime.fromisoformat(
            usd_quote['last_updated'].replace('Z', '+00:00')
        ),
        'priceDirection': (
            'up' if usd_quote['percent_change_24h'] >= 0 else 'down'
        ),
        'marketCapCategory': compute_market_cap_category(
            usd_quote['market_cap']
        ),
    }
