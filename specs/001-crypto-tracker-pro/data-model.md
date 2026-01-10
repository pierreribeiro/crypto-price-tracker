# Data Model: CryptoTracker Pro

**Date**: 2026-01-09
**Phase**: 1 (Design & Contracts)
**Source**: Extracted from [spec.md](./spec.md) requirements

## Overview

This document defines the core data entities for CryptoTracker Pro based on functional requirements. All entities align with Clean Architecture principles (Constitution Principle VII) and support the required features: price tracking, top gainers/losers, search/filter, and trend visualization.

---

## Core Entities

### 1. Cryptocurrency

Represents a digital currency with all attributes needed for display and filtering.

**Entity Definition**:
```typescript
interface Cryptocurrency {
  // Identification
  id: string;                    // Unique identifier from API (e.g., "bitcoin")
  symbol: string;                // Trading symbol (e.g., "BTC")
  name: string;                  // Full name (e.g., "Bitcoin")

  // Current Market Data
  currentPrice: number;          // Current price in USD (FR-002)
  marketCap: number;             // Market capitalization in USD (FR-005)
  volume24h: number;             // 24-hour trading volume in USD (FR-005)

  // Price Changes
  priceChange24h: number;        // Absolute price change in 24h (FR-003)
  priceChangePercent24h: number; // Percentage price change in 24h (FR-003)

  // Trend Data
  sparklineData: PriceDataPoint[]; // 7-day price history for sparkline (FR-011)

  // Metadata
  rank: number;                  // Market cap ranking (FR-001: top 20)
  lastUpdated: Date;             // Timestamp of last data update (FR-015)

  // Computed Properties (not stored, calculated on demand)
  priceDirection: 'up' | 'down'; // Derived from priceChangePercent24h (FR-004)
  marketCapCategory: MarketCategory; // Derived from marketCap (FR-010)
}
```

**Validation Rules** (from requirements):
- `currentPrice` MUST be positive number (business logic)
- `marketCap` MUST be positive number (business logic)
- `volume24h` MUST be non-negative number (can be zero for illiquid assets)
- `priceChangePercent24h` MUST be finite number (can be negative)
- `sparklineData` MUST contain at least 1 data point, maximum 168 (7 days * 24 hours)
- `rank` MUST be 1-20 for top 20 display (FR-001)
- `lastUpdated` MUST be within last 5 minutes for cache validity (FR-016)

**State Transitions**:
None - Cryptocurrency is a value object with no lifecycle states. Updated wholesale on each refresh.

**Relationships**:
- HAS-MANY `PriceDataPoint` for sparkline visualization
- BELONGS-TO `MarketCategory` (computed from marketCap thresholds)

---

### 2. PriceDataPoint

Represents a single price observation at a specific timestamp for building historical trends and charts.

**Entity Definition**:
```typescript
interface PriceDataPoint {
  timestamp: Date;    // ISO 8601 timestamp of observation
  price: number;      // Price in USD at this timestamp
}
```

**Validation Rules**:
- `timestamp` MUST be valid ISO 8601 date
- `price` MUST be positive number
- For sparkline data: timestamps MUST be in chronological order
- For sparkline data: maximum 168 data points (7 days hourly)

**State Transitions**:
None - Immutable value object representing historical observation.

**Relationships**:
- BELONGS-TO `Cryptocurrency` (as part of sparklineData array)

---

### 3. MarketCategory

Classification of cryptocurrencies based on market capitalization size for filtering purposes (FR-010).

**Entity Definition**:
```typescript
enum MarketCategory {
  LARGE_CAP = 'large',   // Market cap > $10B
  MID_CAP = 'mid',       // Market cap $1B - $10B
  SMALL_CAP = 'small'    // Market cap < $1B
}
```

**Validation Rules**:
- Category determined by market cap thresholds:
  - `SMALL_CAP`: marketCap < $1,000,000,000
  - `MID_CAP`: $1,000,000,000 ≤ marketCap ≤ $10,000,000,000
  - `LARGE_CAP`: marketCap > $10,000,000,000

**State Transitions**:
None - Enum/constant values, computed from Cryptocurrency.marketCap.

**Relationships**:
- Referenced by `Cryptocurrency` as computed property

---

## API Response Models

### CoinGecko API Response (Primary Source)

**Endpoint**: `/coins/markets` (for top cryptocurrencies by market cap)

```typescript
interface CoinGeckoMarketResponse {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  total_volume: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  market_cap_rank: number;
  sparkline_in_7d?: {
    price: number[];  // Array of prices for last 7 days
  };
  last_updated: string; // ISO 8601 timestamp
}
```

**Mapping to Cryptocurrency Entity**:
```typescript
function mapCoinGeckoResponse(apiData: CoinGeckoMarketResponse): Cryptocurrency {
  return {
    id: apiData.id,
    symbol: apiData.symbol.toUpperCase(),
    name: apiData.name,
    currentPrice: apiData.current_price,
    marketCap: apiData.market_cap,
    volume24h: apiData.total_volume,
    priceChange24h: apiData.price_change_24h,
    priceChangePercent24h: apiData.price_change_percentage_24h,
    sparklineData: mapSparklineData(apiData.sparkline_in_7d?.price || []),
    rank: apiData.market_cap_rank,
    lastUpdated: new Date(apiData.last_updated),
    priceDirection: apiData.price_change_percentage_24h >= 0 ? 'up' : 'down',
    marketCapCategory: computeMarketCapCategory(apiData.market_cap)
  };
}
```

### CoinMarketCap API Response (Fallback Source)

**Endpoint**: `/cryptocurrency/listings/latest` (for top cryptocurrencies)

```typescript
interface CoinMarketCapResponse {
  data: Array<{
    id: number;
    symbol: string;
    name: string;
    quote: {
      USD: {
        price: number;
        volume_24h: number;
        market_cap: number;
        percent_change_24h: number;
        last_updated: string; // ISO 8601 timestamp
      };
    };
    cmc_rank: number;
  }>;
}
```

**Mapping to Cryptocurrency Entity**:
```typescript
function mapCoinMarketCapResponse(apiData: CoinMarketCapResponse['data'][0]): Cryptocurrency {
  const usd = apiData.quote.USD;
  const priceChange24h = (usd.percent_change_24h / 100) * usd.price; // Compute absolute change

  return {
    id: apiData.symbol.toLowerCase(), // Use symbol as ID since CoinMarketCap uses numeric IDs
    symbol: apiData.symbol,
    name: apiData.name,
    currentPrice: usd.price,
    marketCap: usd.market_cap,
    volume24h: usd.volume_24h,
    priceChange24h: priceChange24h,
    priceChangePercent24h: usd.percent_change_24h,
    sparklineData: [], // CoinMarketCap free tier doesn't provide sparkline data
    rank: apiData.cmc_rank,
    lastUpdated: new Date(usd.last_updated),
    priceDirection: usd.percent_change_24h >= 0 ? 'up' : 'down',
    marketCapCategory: computeMarketCapCategory(usd.market_cap)
  };
}
```

---

## Data Validation Layer

All external API data MUST be validated before display (FR-018). Implement validation service:

```typescript
interface ValidationResult {
  isValid: boolean;
  errors: string[];
  data?: Cryptocurrency;
}

function validateCryptocurrency(data: any): ValidationResult {
  const errors: string[] = [];

  // Required fields
  if (!data.id || typeof data.id !== 'string') {
    errors.push('Missing or invalid id');
  }
  if (!data.symbol || typeof data.symbol !== 'string') {
    errors.push('Missing or invalid symbol');
  }
  if (!data.name || typeof data.name !== 'string') {
    errors.push('Missing or invalid name');
  }

  // Numeric validations
  if (typeof data.currentPrice !== 'number' || data.currentPrice <= 0) {
    errors.push('Invalid currentPrice: must be positive number');
  }
  if (typeof data.marketCap !== 'number' || data.marketCap <= 0) {
    errors.push('Invalid marketCap: must be positive number');
  }
  if (typeof data.volume24h !== 'number' || data.volume24h < 0) {
    errors.push('Invalid volume24h: must be non-negative number');
  }

  // Percentage validations
  if (typeof data.priceChangePercent24h !== 'number' || !isFinite(data.priceChangePercent24h)) {
    errors.push('Invalid priceChangePercent24h: must be finite number');
  }

  // Rank validation
  if (typeof data.rank !== 'number' || data.rank < 1 || data.rank > 20) {
    errors.push('Invalid rank: must be between 1 and 20');
  }

  // Date validation
  if (!(data.lastUpdated instanceof Date) || isNaN(data.lastUpdated.getTime())) {
    errors.push('Invalid lastUpdated: must be valid Date');
  }

  // Sparkline validation
  if (!Array.isArray(data.sparklineData)) {
    errors.push('Invalid sparklineData: must be array');
  } else if (data.sparklineData.length > 168) {
    errors.push('Invalid sparklineData: maximum 168 data points allowed');
  }

  return {
    isValid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data : undefined
  };
}
```

---

## Caching Strategy

Per FR-016, implement 5-minute TTL caching in Redis:

**Cache Key Structure**:
```
crypto:list:top20           → List of top 20 cryptocurrencies (TTL: 5 minutes)
crypto:details:{id}         → Individual cryptocurrency details (TTL: 5 minutes)
crypto:gainers:top20        → Top 20 gainers list (TTL: 5 minutes)
crypto:losers:top20         → Top 20 losers list (TTL: 5 minutes)
crypto:sparkline:{id}       → 7-day sparkline data (TTL: 1 hour - less volatile)
```

**Cache Invalidation**:
- All cache entries use TTL-based expiration (no manual invalidation)
- On cache miss or expiration, fetch from CoinGecko API (primary)
- On CoinGecko failure, attempt CoinMarketCap API (fallback per FR-022)
- On both API failures, return cached data with warning (per Edge Case: API unavailability)

---

## Data Flow Diagram

```
External APIs (CoinGecko / CoinMarketCap)
    ↓
API Client Layer (with retry + fallback logic)
    ↓
Validation Layer (validateCryptocurrency)
    ↓
Mapping Layer (API response → Cryptocurrency entity)
    ↓
Cache Layer (Redis with 5-min TTL)
    ↓
Service Layer (business logic: sorting, filtering, search)
    ↓
API Endpoints (REST + WebSocket)
    ↓
Frontend (React components)
```

---

## Data Transformation Examples

### Example 1: Top Gainers Calculation

From FR-006: Top 20 cryptocurrencies ranked by 24h percentage gain.

```typescript
function getTopGainers(cryptos: Cryptocurrency[]): Cryptocurrency[] {
  return cryptos
    .filter(c => c.priceChangePercent24h > 0) // Only positive changes
    .sort((a, b) => b.priceChangePercent24h - a.priceChangePercent24h) // Descending
    .slice(0, 20); // Top 20
}
```

### Example 2: Search Implementation

From FR-008: Search cryptocurrencies by name or symbol.

```typescript
function searchCryptocurrencies(
  cryptos: Cryptocurrency[],
  query: string
): Cryptocurrency[] {
  const lowerQuery = query.toLowerCase();
  return cryptos.filter(c =>
    c.name.toLowerCase().includes(lowerQuery) ||
    c.symbol.toLowerCase().includes(lowerQuery)
  );
}
```

### Example 3: Price Range Filter

From FR-009: Filter cryptocurrencies by price range.

```typescript
function filterByPriceRange(
  cryptos: Cryptocurrency[],
  minPrice: number,
  maxPrice: number
): Cryptocurrency[] {
  return cryptos.filter(c =>
    c.currentPrice >= minPrice && c.currentPrice <= maxPrice
  );
}
```

### Example 4: Market Cap Category Filter

From FR-010: Filter by market cap category.

```typescript
function filterByMarketCapCategory(
  cryptos: Cryptocurrency[],
  category: MarketCategory
): Cryptocurrency[] {
  return cryptos.filter(c => c.marketCapCategory === category);
}
```

---

## Edge Case Handling

### Malformed API Data (Edge Case: API responses contain malformed or missing data)

**Strategy**: Validate all incoming data with `validateCryptocurrency()`. Filter out invalid entries, log errors for debugging, display only valid cryptocurrency information without crashing (per Edge Case requirement).

```typescript
function processAPIResponse(apiData: any[]): Cryptocurrency[] {
  const validCryptos: Cryptocurrency[] = [];
  const errors: Array<{id: string, errors: string[]}> = [];

  for (const item of apiData) {
    const validation = validateCryptocurrency(mapAPIResponse(item));
    if (validation.isValid && validation.data) {
      validCryptos.push(validation.data);
    } else {
      errors.push({ id: item.id || 'unknown', errors: validation.errors });
      console.error('Invalid cryptocurrency data:', validation.errors);
    }
  }

  // Log aggregate errors for monitoring
  if (errors.length > 0) {
    console.warn(`Filtered ${errors.length} invalid cryptocurrencies from API response`);
  }

  return validCryptos;
}
```

### Extremely Large/Small Prices (Edge Case: Displaying extremely large or small cryptocurrency prices)

**Strategy**: Format numbers appropriately using scientific notation or abbreviated formats (K, M, B, T) for readability while maintaining precision for calculations (per Edge Case requirement).

```typescript
function formatPrice(price: number): string {
  if (price >= 1_000_000_000_000) {
    return `$${(price / 1_000_000_000_000).toFixed(2)}T`;
  } else if (price >= 1_000_000_000) {
    return `$${(price / 1_000_000_000).toFixed(2)}B`;
  } else if (price >= 1_000_000) {
    return `$${(price / 1_000_000).toFixed(2)}M`;
  } else if (price >= 1_000) {
    return `$${(price / 1_000).toFixed(2)}K`;
  } else if (price < 0.01) {
    return `$${price.toExponential(4)}`; // Scientific notation for very small prices
  } else {
    return `$${price.toFixed(2)}`;
  }
}

function formatMarketCap(marketCap: number): string {
  return formatPrice(marketCap); // Reuse price formatting for market cap
}
```

---

## Summary

This data model provides a clean, validated structure for CryptoTracker Pro that:
- Satisfies all functional requirements (FR-001 through FR-024)
- Implements validation for API data quality (FR-018)
- Supports caching strategy with 5-minute TTL (FR-016)
- Handles edge cases gracefully (malformed data, extreme values)
- Aligns with Clean Architecture (Constitution Principle VII)
- Enables efficient filtering, sorting, and search operations

**Next Steps**: Generate API contracts in `/contracts/` directory defining REST endpoints and WebSocket message formats.
