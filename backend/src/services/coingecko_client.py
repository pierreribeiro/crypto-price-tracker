"""
CoinGecko API client with rate limiting

Primary data source for cryptocurrency data (FR-022)
Constitution Principle III: API Reliability with retry logic
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from src.lib.retry import retry_api_call


class CoinGeckoClient:
    """
    Client for CoinGecko API

    Provides methods to fetch cryptocurrency data with rate limiting
    and retry logic for reliability
    """

    def __init__(self) -> None:
        """Initialize CoinGecko client with API key and base URL"""
        self.api_key = os.getenv('COINGECKO_API_KEY', '')
        self.base_url = 'https://api.coingecko.com/api/v3'

        # Set up headers
        self.headers = {
            'Accept': 'application/json',
        }
        if self.api_key:
            self.headers['x-cg-demo-api-key'] = self.api_key

        # Rate limiting: CoinGecko free tier allows 10-50 calls/minute
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    @retry_api_call
    async def get_top_cryptocurrencies(
        self, limit: int = 20, include_sparkline: bool = True
    ) -> list[dict[str, Any]]:
        """
        Fetch top cryptocurrencies by market cap

        Implements FR-001: Display top 20 cryptocurrencies

        Args:
            limit: Number of cryptocurrencies to fetch (default: 20)
            include_sparkline: Include 7-day sparkline data (default: True)

        Returns:
            List of cryptocurrency data dictionaries

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            httpx.TimeoutException: On request timeout
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f'{self.base_url}/coins/markets',
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': limit,
                    'page': 1,
                    'sparkline': str(include_sparkline).lower(),
                    'price_change_percentage': '24h',
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    @retry_api_call
    async def get_cryptocurrency_by_id(
        self, crypto_id: str
    ) -> dict[str, Any]:
        """
        Fetch detailed information for a specific cryptocurrency

        Args:
            crypto_id: Cryptocurrency ID (e.g., 'bitcoin')

        Returns:
            Cryptocurrency data dictionary

        Raises:
            httpx.HTTPStatusError: On HTTP errors (404 if not found)
            httpx.TimeoutException: On request timeout
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f'{self.base_url}/coins/{crypto_id}',
                params={
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false',
                    'sparkline': 'true',
                },
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    @retry_api_call
    async def ping(self) -> bool:
        """
        Ping CoinGecko API to check availability

        Returns:
            True if API is available, False otherwise
        """
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0)
            ) as client:
                response = await client.get(
                    f'{self.base_url}/ping', headers=self.headers
                )
                response.raise_for_status()
                return True
        except Exception as e:
            print(f'⚠️  CoinGecko API ping failed: {e}')
            return False


def map_coingecko_response(api_data: dict[str, Any]) -> dict[str, Any]:
    """
    Map CoinGecko API response to internal Cryptocurrency model

    From data-model.md mapping specification

    Args:
        api_data: Raw CoinGecko API response data

    Returns:
        Mapped cryptocurrency data matching internal model
    """
    from src.lib.formatters import compute_market_cap_category

    # Extract sparkline data if available
    sparkline_prices = (
        api_data.get('sparkline_in_7d', {}).get('price', [])
        if 'sparkline_in_7d' in api_data
        else []
    )

    return {
        'id': api_data['id'],
        'symbol': api_data['symbol'].upper(),
        'name': api_data['name'],
        'currentPrice': api_data['current_price'],
        'marketCap': api_data['market_cap'],
        'volume24h': api_data['total_volume'],
        'priceChange24h': api_data['price_change_24h'],
        'priceChangePercent24h': api_data['price_change_percentage_24h'],
        'sparklineData': map_sparkline_data(sparkline_prices),
        'rank': api_data['market_cap_rank'],
        'lastUpdated': datetime.fromisoformat(
            api_data['last_updated'].replace('Z', '+00:00')
        ),
        'priceDirection': (
            'up' if api_data['price_change_percentage_24h'] >= 0 else 'down'
        ),
        'marketCapCategory': compute_market_cap_category(
            api_data['market_cap']
        ),
    }


def map_sparkline_data(prices: list[float]) -> list[dict[str, Any]]:
    """
    Map sparkline price array to PriceDataPoint list

    From data-model.md: Sparkline contains hourly prices for last 7 days

    Args:
        prices: Array of prices (one per hour for 7 days, up to 168 points)

    Returns:
        List of PriceDataPoint dictionaries with timestamp and price
    """
    if not prices:
        return []

    # Calculate timestamps: assume prices are hourly, ending at current time
    now = datetime.now(timezone.utc)
    price_data_points: list[dict[str, Any]] = []

    for i, price in enumerate(prices):
        # Calculate timestamp: start from (now - len(prices) hours) + i hours
        hours_ago = len(prices) - i - 1
        timestamp = now.replace(
            minute=0, second=0, microsecond=0
        ) - timedelta(hours=hours_ago)

        price_data_points.append({'timestamp': timestamp, 'price': price})

    return price_data_points
