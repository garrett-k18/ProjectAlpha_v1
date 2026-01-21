/**
 * BADGE SYSTEM - PUBLIC API
 * ============================================================================
 *
 * Single import point for all badge-related functionality
 *
 * Usage:
 * ```typescript
 * import {
 *   BadgeToneKey,
 *   BadgeSizeKey,
 *   resolveBadgeTokens,
 *   getPropertyTypeBadgeTone,
 *   propertyTypeEnumMap
 * } from '@/GlobalStandardizations/badges'
 * ```
 *
 * ============================================================================
 */

// ============================================================================
// CONFIG EXPORTS
// ============================================================================

export {
  BADGE_DIMENSIONS,
  BADGE_SIZE_CONFIG,
  toYesNoLabel,
} from './badgeConfig';

export type {
  BadgeSizeKey,
  BadgeVisualConfig,
  BadgeTokenResult,
} from './badgeConfig';

// ============================================================================
// COLOR EXPORTS
// ============================================================================

export {
  BADGE_TONE_CONFIG,
  createPaletteBadge,
  PROPERTY_TYPE_COLORS,
  ASSET_MASTER_STATUS_COLORS,
  LOAN_PERFORMANCE_COLORS,
  ASSET_PIPELINE_TRACK_COLORS,
} from './badgeColors';

export type {
  BadgeToneKey,
} from './badgeColors';

// ============================================================================
// HELPER EXPORTS
// ============================================================================

export {
  // Core function
  resolveBadgeTokens,

  // Field-to-tone mapping functions
  getOccupancyBadgeTone,
  getAssetStatusBadgeTone,
  getProductTypeBadgeTone,
  getPropertyTypeBadgeTone,
  getDelinquencyBadgeTone,
  getCalendarEventBadgeTone,
  getCalendarEventColors,
  getLifecycleBadgeTone,

  // Flag badge helpers
  getFcFlagBadgeTone,
  getBkFlagBadgeTone,
  getModFlagBadgeTone,

  // AG Grid enum map generators
  getPropertyTypeEnumMap,
  getAssetMasterStatusEnumMap,
  getLoanPerformanceEnumMap,
  getAssetPipelineTrackEnumMap,
  getAssetPipelineTrackColorMap,

  // Predefined enum maps
  propertyTypeEnumMap,
  occupancyEnumMap,
  assetStatusEnumMap,
  productTypeEnumMap,
  activeTracksEnumMap,
  activeTasksColorMap,
  foreclosureFlagEnumMap,
  bankruptcyFlagEnumMap,
  modificationFlagEnumMap,

  // Property type lookup
  propertyTypeToneLookup,
} from './badgeHelpers';
