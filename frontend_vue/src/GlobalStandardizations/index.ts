/**
 * GLOBAL STANDARDIZATIONS - PUBLIC API
 * ============================================================================
 *
 * Central export point for all global UI standardizations
 *
 * Usage:
 * ```typescript
 * // Import from specific modules (recommended)
 * import { resolveBadgeTokens } from '@/GlobalStandardizations/badges'
 * import { getStatusColor } from '@/GlobalStandardizations/colors'
 *
 * // Or import from root (if you need multiple things)
 * import { resolveBadgeTokens, getStatusColor } from '@/GlobalStandardizations'
 * ```
 *
 * ============================================================================
 */

// ============================================================================
// BADGE SYSTEM
// ============================================================================
export * from './badges';

// ============================================================================
// COLOR SYSTEM
// ============================================================================
export * from './colors';

// ============================================================================
// UI TOKENS (Spacing, Typography, Shadows, etc.)
// ============================================================================
export * from './ui';
