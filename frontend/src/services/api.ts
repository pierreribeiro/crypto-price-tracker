/**
 * API client service for CryptoTracker Pro
 *
 * Handles HTTP requests to the backend API
 * Constitution Principle III: API Reliability
 */

import type {
  CryptocurrencyListResponse,
  Cryptocurrency,
  HealthCheckResponse,
} from '../../../shared/types/api';

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * Generic API request handler with error handling
 */
async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      // Parse error response if available
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.message || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    // Re-throw with additional context
    if (error instanceof Error) {
      throw new Error(`API request failed: ${error.message}`);
    }
    throw new Error('Unknown API error occurred');
  }
}

/**
 * Fetch top 20 cryptocurrencies by market cap
 * Implements FR-001, FR-002, FR-003, FR-004, FR-005
 */
export async function getTopCryptocurrencies(
  includeSparkline: boolean = true
): Promise<CryptocurrencyListResponse> {
  const params = new URLSearchParams({
    include_sparkline: includeSparkline.toString(),
  });

  return apiRequest<CryptocurrencyListResponse>(
    `/cryptocurrencies?${params.toString()}`
  );
}

/**
 * Fetch top 20 gainers
 * Implements FR-006
 */
export async function getTopGainers(
  includeSparkline: boolean = false
): Promise<CryptocurrencyListResponse> {
  const params = new URLSearchParams({
    include_sparkline: includeSparkline.toString(),
  });

  return apiRequest<CryptocurrencyListResponse>(
    `/cryptocurrencies/gainers?${params.toString()}`
  );
}

/**
 * Fetch top 20 losers
 * Implements FR-007
 */
export async function getTopLosers(
  includeSparkline: boolean = false
): Promise<CryptocurrencyListResponse> {
  const params = new URLSearchParams({
    include_sparkline: includeSparkline.toString(),
  });

  return apiRequest<CryptocurrencyListResponse>(
    `/cryptocurrencies/losers?${params.toString()}`
  );
}

/**
 * Search cryptocurrencies with optional filters
 * Implements FR-008, FR-009, FR-010
 */
export async function searchCryptocurrencies(params: {
  query: string;
  minPrice?: number;
  maxPrice?: number;
  marketCapCategory?: 'small' | 'mid' | 'large';
  includeSparkline?: boolean;
}): Promise<CryptocurrencyListResponse> {
  const searchParams = new URLSearchParams({
    q: params.query,
  });

  if (params.minPrice !== undefined) {
    searchParams.append('min_price', params.minPrice.toString());
  }
  if (params.maxPrice !== undefined) {
    searchParams.append('max_price', params.maxPrice.toString());
  }
  if (params.marketCapCategory) {
    searchParams.append('market_cap_category', params.marketCapCategory);
  }
  if (params.includeSparkline !== undefined) {
    searchParams.append('include_sparkline', params.includeSparkline.toString());
  }

  return apiRequest<CryptocurrencyListResponse>(
    `/cryptocurrencies/search?${searchParams.toString()}`
  );
}

/**
 * Fetch detailed information for a specific cryptocurrency
 * Implements FR-012
 */
export async function getCryptocurrencyById(id: string): Promise<Cryptocurrency> {
  return apiRequest<Cryptocurrency>(`/cryptocurrencies/${id}`);
}

/**
 * Check API health status
 */
export async function getHealthCheck(): Promise<HealthCheckResponse> {
  return apiRequest<HealthCheckResponse>('/health');
}
