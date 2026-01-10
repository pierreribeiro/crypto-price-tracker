/**
 * Skeleton Screen component
 *
 * Loading placeholder for cryptocurrency cards
 * FR-024: Show skeleton screen while loading data
 * Constitution Principle IV: Mobile-First responsive design
 */

import './SkeletonScreen.css';

export interface SkeletonScreenProps {
  /** Number of skeleton cards to display */
  count?: number;
}

/**
 * Skeleton loading component
 *
 * Displays animated placeholders while cryptocurrency data is loading
 * Improves perceived performance and user experience
 */
export function SkeletonScreen({ count = 20 }: SkeletonScreenProps) {
  return (
    <div className="skeleton-grid">
      {Array.from({ length: count }, (_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  );
}

/**
 * Single skeleton card placeholder
 */
function SkeletonCard() {
  return (
    <div className="skeleton-card">
      {/* Crypto icon */}
      <div className="skeleton-avatar" />

      {/* Name and symbol */}
      <div className="skeleton-content">
        <div className="skeleton-line skeleton-line-lg" />
        <div className="skeleton-line skeleton-line-sm" />
      </div>

      {/* Price */}
      <div className="skeleton-content">
        <div className="skeleton-line skeleton-line-md" />
      </div>

      {/* 24h change */}
      <div className="skeleton-content">
        <div className="skeleton-line skeleton-line-sm" />
      </div>

      {/* Market cap */}
      <div className="skeleton-content">
        <div className="skeleton-line skeleton-line-md" />
      </div>
    </div>
  );
}
