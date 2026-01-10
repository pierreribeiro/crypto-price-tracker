/**
 * Number formatting utilities for cryptocurrency data
 *
 * Handles edge case: Displaying extremely large or small cryptocurrency prices
 * Constitution Principle II: Type Safety
 */

/**
 * Format cryptocurrency price with appropriate precision
 *
 * Handles extremely large and small prices with abbreviated formats or
 * scientific notation for readability
 */
export function formatPrice(price: number, decimals: number = 2): string {
  if (price >= 1_000_000_000_000) {
    // Trillions
    return `$${(price / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (price >= 1_000_000_000) {
    // Billions
    return `$${(price / 1_000_000_000).toFixed(2)}B`;
  }
  if (price >= 1_000_000) {
    // Millions
    return `$${(price / 1_000_000).toFixed(2)}M`;
  }
  if (price >= 1_000) {
    // Thousands
    return `$${(price / 1_000).toFixed(2)}K`;
  }
  if (price < 0.01) {
    // Very small prices - use scientific notation
    return `$${price.toExponential(4)}`;
  }
  // Standard formatting with thousands separator
  return `$${price.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

/**
 * Format market capitalization with abbreviated notation
 */
export function formatMarketCap(marketCap: number): string {
  return formatPrice(marketCap);
}

/**
 * Format 24-hour trading volume with abbreviated notation
 */
export function formatVolume(volume: number): string {
  return formatPrice(volume);
}

/**
 * Format percentage change with optional +/- sign
 */
export function formatPercentage(
  percentage: number,
  decimals: number = 2,
  includeSign: boolean = true
): string {
  const formatted = Math.abs(percentage).toFixed(decimals);

  if (includeSign) {
    const sign = percentage >= 0 ? '+' : '-';
    return `${sign}${formatted}%`;
  }

  return `${formatted}%`;
}

/**
 * Format date to human-readable string
 */
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

/**
 * Format date to relative time (e.g., "2 minutes ago")
 */
export function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);

  if (diffMinutes < 1) {
    return 'Just now';
  }
  if (diffMinutes === 1) {
    return '1 minute ago';
  }
  if (diffMinutes < 60) {
    return `${diffMinutes} minutes ago`;
  }

  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours === 1) {
    return '1 hour ago';
  }
  if (diffHours < 24) {
    return `${diffHours} hours ago`;
  }

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) {
    return '1 day ago';
  }
  return `${diffDays} days ago`;
}

/**
 * Format any large number with compact notation (K/M/B/T)
 */
export function formatNumberCompact(value: number): string {
  if (value >= 1_000_000_000_000) {
    return `${(value / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(2)}B`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (value >= 1_000) {
    return `${(value / 1_000).toFixed(2)}K`;
  }
  return value.toFixed(2);
}
