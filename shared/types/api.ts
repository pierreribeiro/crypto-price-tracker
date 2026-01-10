/**
 * API response type definitions for CryptoTracker Pro
 * Based on api-specification.yaml OpenAPI contract
 *
 * Constitution Principle II: Type Safety
 */

import { Cryptocurrency } from './cryptocurrency';

/**
 * Data source for cryptocurrency information
 * Indicates which external API or cache provided the data (FR-022)
 */
export type DataSource = 'coingecko' | 'coinmarketcap' | 'cache';

/**
 * API health status indicator
 */
export type HealthStatus = 'healthy' | 'degraded';

/**
 * External API availability status
 */
export type ApiAvailability = 'available' | 'unavailable';

/**
 * Metadata included with cryptocurrency list responses
 * Provides context about the data: count, freshness, and source
 */
export interface ResponseMetadata {
  /** Number of cryptocurrencies in response (0-20) */
  count: number;

  /** ISO 8601 timestamp of last data update (FR-015) */
  lastUpdated: string;

  /** Source of data: CoinGecko, CoinMarketCap, or cache (FR-022) */
  dataSource: DataSource;

  /** Whether response was served from cache */
  cacheHit: boolean;
}

/**
 * Standard response format for cryptocurrency list endpoints
 * Used by:
 * - GET /api/v1/cryptocurrencies
 * - GET /api/v1/cryptocurrencies/gainers
 * - GET /api/v1/cryptocurrencies/losers
 * - GET /api/v1/cryptocurrencies/search
 */
export interface CryptocurrencyListResponse {
  /** Array of cryptocurrencies (maximum 20 items) */
  data: Cryptocurrency[];

  /** Response metadata */
  metadata: ResponseMetadata;

  /** Optional warning message for degraded service (503 responses) */
  warning?: string;
}

/**
 * Standard error response format
 * Returned by all endpoints on error conditions (FR-019)
 */
export interface ErrorResponse {
  /** Human-readable error message (FR-019) */
  message: string;

  /** Machine-readable error code for programmatic handling */
  code?: string;

  /** ISO 8601 timestamp when error occurred */
  timestamp: string;

  /** Additional error context (optional) */
  details?: Record<string, unknown>;
}

/**
 * Cache connection status for health check
 */
export interface CacheStatus {
  /** Whether Redis is connected */
  connected: boolean;

  /** Redis latency in milliseconds */
  latency_ms?: number;
}

/**
 * External API availability status for health check
 */
export interface ExternalApiStatus {
  /** CoinGecko API availability */
  coingecko: ApiAvailability;

  /** CoinMarketCap API availability */
  coinmarketcap: ApiAvailability;
}

/**
 * Health check response from GET /api/v1/health
 * Indicates overall system health and dependency status
 */
export interface HealthCheckResponse {
  /** Overall health status */
  status: HealthStatus;

  /** ISO 8601 timestamp of health check */
  timestamp: string;

  /** Cache (Redis) connection status */
  cache: CacheStatus;

  /** External API availability status */
  external_apis: ExternalApiStatus;
}

/**
 * WebSocket message type for real-time price updates
 * See websocket-spec.md for full WebSocket protocol
 */
export interface WebSocketPriceUpdate {
  /** Message type identifier */
  type: 'price_update';

  /** Updated cryptocurrency data */
  data: Cryptocurrency;

  /** ISO 8601 timestamp of update */
  timestamp: string;
}

/**
 * WebSocket error message
 */
export interface WebSocketError {
  /** Message type identifier */
  type: 'error';

  /** Error message */
  message: string;

  /** Error code */
  code?: string;

  /** ISO 8601 timestamp */
  timestamp: string;
}

/**
 * WebSocket connection acknowledgment
 */
export interface WebSocketAck {
  /** Message type identifier */
  type: 'connected';

  /** Connection message */
  message: string;

  /** ISO 8601 timestamp */
  timestamp: string;
}

/**
 * Union type for all WebSocket messages
 */
export type WebSocketMessage = WebSocketPriceUpdate | WebSocketError | WebSocketAck;
