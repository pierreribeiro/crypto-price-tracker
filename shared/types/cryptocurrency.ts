/**
 * Shared TypeScript type definitions for CryptoTracker Pro
 * These types are used across both frontend and backend
 *
 * Source: data-model.md
 * Constitution Principle II: Type Safety
 */

/**
 * Represents a single price observation at a specific timestamp
 * Used for building historical trends and sparkline charts
 */
export interface PriceDataPoint {
  /** ISO 8601 timestamp of observation */
  timestamp: Date;

  /** Price in USD at this timestamp (must be positive) */
  price: number;
}

/**
 * Classification of cryptocurrencies based on market capitalization
 * Used for filtering purposes (FR-010)
 */
export enum MarketCategory {
  /** Market cap > $10B */
  LARGE_CAP = 'large',

  /** Market cap $1B - $10B */
  MID_CAP = 'mid',

  /** Market cap < $1B */
  SMALL_CAP = 'small',
}

/**
 * Represents a digital currency with all attributes needed for display and filtering
 * Core entity for the application
 */
export interface Cryptocurrency {
  // Identification
  /** Unique identifier from API (e.g., "bitcoin") */
  id: string;

  /** Trading symbol (e.g., "BTC") */
  symbol: string;

  /** Full name (e.g., "Bitcoin") */
  name: string;

  // Current Market Data
  /** Current price in USD (FR-002) - must be positive */
  currentPrice: number;

  /** Market capitalization in USD (FR-005) - must be positive */
  marketCap: number;

  /** 24-hour trading volume in USD (FR-005) - must be non-negative */
  volume24h: number;

  // Price Changes
  /** Absolute price change in 24h (FR-003) */
  priceChange24h: number;

  /** Percentage price change in 24h (FR-003) - must be finite */
  priceChangePercent24h: number;

  // Trend Data
  /** 7-day price history for sparkline chart (FR-011) */
  sparklineData: PriceDataPoint[];

  // Metadata
  /** Market cap ranking (FR-001: top 20) - must be 1-20 */
  rank: number;

  /** Timestamp of last data update (FR-015) */
  lastUpdated: Date;

  // Computed Properties (calculated on demand, not stored)
  /** Derived from priceChangePercent24h (FR-004) */
  priceDirection: 'up' | 'down';

  /** Derived from marketCap thresholds (FR-010) */
  marketCapCategory: MarketCategory;
}

/**
 * Compute market cap category based on market capitalization value
 *
 * @param marketCap - Market capitalization in USD
 * @returns Market category classification
 */
export function computeMarketCapCategory(marketCap: number): MarketCategory {
  if (marketCap > 10_000_000_000) {
    return MarketCategory.LARGE_CAP;
  }
  if (marketCap >= 1_000_000_000) {
    return MarketCategory.MID_CAP;
  }
  return MarketCategory.SMALL_CAP;
}
