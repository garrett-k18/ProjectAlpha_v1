/**
 * BADGE HELPERS - Utility Functions
 * ============================================================================
 *
 * WHAT: Helper functions for badge token resolution and field-to-badge mappings
 * WHY: Centralized logic for converting field values to appropriate badge tones
 * HOW: Import and use these functions in components for consistent badge rendering
 *
 * ============================================================================
 */

import { getTagColor } from '../colors/colorPalette';
import type { BadgeToneKey } from './badgeColors';
import { BADGE_TONE_CONFIG } from './badgeColors';
import type { BadgeSizeKey, BadgeTokenResult } from './badgeConfig';
import {
  BADGE_SIZE_CONFIG,
  toYesNoLabel,
} from './badgeConfig';
import {
  PROPERTY_TYPE_COLORS,
  ASSET_MASTER_STATUS_COLORS,
  LOAN_PERFORMANCE_COLORS,
  ASSET_PIPELINE_TRACK_COLORS,
} from './badgeColors';

// ============================================================================
// 🔧 CORE TOKEN RESOLUTION
// ============================================================================

/**
 * SINGLE SOURCE OF TRUTH: Merge tone and size definitions into complete badge config
 * WHAT: Combines size + tone configs into complete badge styling
 * WHY: Eliminates need for dual styling in component files
 * HOW: Merges classes and inline styles from both size and tone configs
 *
 * @param toneKey - Badge tone key (color theme)
 * @param sizeKey - Badge size key (xs, sm, md, lg)
 * @returns Complete badge configuration with merged classes and styles
 */
export function resolveBadgeTokens(
  toneKey: BadgeToneKey,
  sizeKey: BadgeSizeKey = 'md',
): BadgeTokenResult {
  const tone = BADGE_TONE_CONFIG[toneKey];
  const size = BADGE_SIZE_CONFIG[sizeKey];

  // Merge inline styles from both size and tone
  // Ensure proper semicolon separation for CSS
  const mergedStyles = [size.inlineStyles, tone.inlineStyles]
    .filter(Boolean)
    .map(s => s?.trim())
    .filter(s => s && s.length > 0)
    .join(' ');

  return {
    classes: `${size.classes} ${tone.classes}`.trim(),
    ariaLabel: tone.ariaLabel ?? size.ariaLabel,
    inlineStyles: mergedStyles || undefined,
  };
}

// ============================================================================
// 🗺️ FIELD VALUE MAPPINGS - Convert field values to badge tones
// ============================================================================

/**
 * Map occupancy values to badge tones
 * @param occupancy - Occupancy status string
 * @returns Badge tone key
 */
export function getOccupancyBadgeTone(occupancy?: string | null): BadgeToneKey {
  const v = (occupancy ?? '').toString().toLowerCase();
  if (v === 'occupied') return 'success';
  if (v === 'vacant') return 'danger';
  if (v === 'unknown') return 'warning';
  return 'secondary';
}

/**
 * Map asset status (NPL/REO/PERF/RPL) to badge tones
 * @param status - Asset status string
 * @returns Badge tone key
 */
export function getAssetStatusBadgeTone(status?: string | null): BadgeToneKey {
  const v = (status ?? '').toString().toUpperCase();
  if (v === 'NPL') return 'danger';
  if (v === 'REO') return 'secondary';
  if (v === 'PERF') return 'success';
  if (v === 'RPL') return 'info';
  return 'secondary';
}

/**
 * Map product type strings to badge tones
 * @param productType - Product type string
 * @returns Badge tone key
 */
export function getProductTypeBadgeTone(productType?: string | null): BadgeToneKey {
  const v = (productType ?? '').toString().toLowerCase();
  switch (v) {
    case 'bpl':
      return 'primary';
    case 'hecm':
      return 'info';
    case 'va':
      return 'success';
    case 'conv':
      return 'dark';
    case 'commercial':
      return 'secondary';
    default:
      return 'secondary';
  }
}

/**
 * Normalized lookup for property type strings to badge tone keys
 */
export const propertyTypeToneLookup: Record<string, BadgeToneKey> = {
  // Single Family Residence (Blue/Primary)
  sfr: 'property-sfr',
  'single family': 'property-sfr',
  'single-family': 'property-sfr',
  manufactured: 'property-sfr',
  'mobile home': 'property-sfr',

  // Condo (Cyan/Info)
  condo: 'property-condo',
  condominium: 'property-condo',

  // Townhome (Purple/Secondary)
  townhome: 'property-townhome',
  townhouse: 'property-townhome',
  'town home': 'property-townhome',
  'town house': 'property-townhome',

  // Multifamily (Green/Success)
  '2-4 family': 'property-multifamily',
  '2-4': 'property-multifamily',
  'multifamily 5+': 'property-multifamily',
  multifamily: 'property-multifamily',
  'multi-family': 'property-multifamily',
  duplex: 'property-multifamily',
  triplex: 'property-multifamily',
  fourplex: 'property-multifamily',

  // Land (Yellow/Warning)
  land: 'property-land',
  lot: 'property-land',
  'vacant land': 'property-land',

  // Mixed Use (Purple)
  'mixed use': 'property-mixed-use',
  'mixed-use': 'property-mixed-use',
  commercial: 'property-mixed-use',

  // Industrial/Storage/Other (Dark)
  industrial: 'property-other',
  warehouse: 'property-other',
  storage: 'property-other',
  'self-storage': 'property-other',
  retail: 'property-other',
  office: 'property-other',
};

/**
 * Helper that resolves a property type string to an appropriate badge tone key
 * @param propertyType - Property type string
 * @returns Badge tone key
 */
export function getPropertyTypeBadgeTone(propertyType?: string | null): BadgeToneKey {
  if (!propertyType) {
    return 'property-other';
  }
  const normalized = propertyType.trim().toLowerCase();
  return propertyTypeToneLookup[normalized] ?? 'property-other';
}

/**
 * Helper that maps delinquency buckets to badge tone keys
 * @param status - Delinquency status string
 * @returns Badge tone key
 */
export function getDelinquencyBadgeTone(status?: string | null): BadgeToneKey {
  switch ((status ?? '').toLowerCase()) {
    case 'current':
      return 'delinquency-current';
    case '30':
    case '30d':
      return 'delinquency-30';
    case '60':
    case '60d':
      return 'delinquency-60';
    case '90':
    case '90d':
      return 'delinquency-90';
    case '120_plus':
    case '120+':
    case '120d':
      return 'delinquency-120-plus';
    default:
      return 'delinquency-current';
  }
}

/**
 * Helper that maps calendar event types to badge tone keys
 * @param eventType - Calendar event type string
 * @returns Badge tone key
 */
export function getCalendarEventBadgeTone(eventType?: string | null): BadgeToneKey {
  switch ((eventType ?? '').toLowerCase()) {
    case 'actual_liquidation':
      return 'calendar-liquidation';
    case 'projected_liquidation':
      return 'calendar-projected';
    case 'bid_date':
    case 'trade': // Trade events use the same color as bid_date (Steel Teal)
      return 'calendar-bid';
    case 'settlement_date':
      return 'calendar-settlement';
    case 'follow_up':
      return 'calendar-follow-up';
    case 'milestone':
      return 'calendar-milestone';
    default:
      return 'calendar-milestone';
  }
}

/**
 * Helper that maps calendar event types to CSS colors for FullCalendar
 * Returns hex color values matching the ProjectAlpha palette
 * @param eventType - Calendar event type string
 * @returns Object with bg, border, and text color hex values
 */
export function getCalendarEventColors(eventType?: string | null): { bg: string; border: string; text: string } {
  switch ((eventType ?? '').toLowerCase()) {
    case 'actual_liquidation':
      return { bg: '#00796B', border: '#00796B', text: '#ffffff' }; // Info Teal
    case 'projected_liquidation':
      return { bg: '#6B5A7A', border: '#6B5A7A', text: '#ffffff' }; // Muted Plum
    case 'bid_date':
    case 'trade': // Trade events use the same color as bid_date (Steel Teal #4A7A8A)
      return { bg: '#4A7A8A', border: '#4A7A8A', text: '#ffffff' }; // Steel Teal
    case 'settlement_date':
      return { bg: '#5A8A95', border: '#5A8A95', text: '#ffffff' }; // Slate Teal
    case 'follow_up':
      return { bg: '#3F51B5', border: '#3F51B5', text: '#ffffff' }; // Indigo
    case 'milestone':
    default:
      return { bg: '#8A7A9A', border: '#8A7A9A', text: '#ffffff' }; // Dusty Lavender
  }
}

/**
 * Helper that maps lifecycle statuses (Active, Liquidated, etc.) to badge tones
 * @param status - Lifecycle status string
 * @returns Badge tone key
 */
export function getLifecycleBadgeTone(status?: string | null): BadgeToneKey {
  const normalized = (status ?? '').toString().trim().toLowerCase();
  if (!normalized) {
    return 'lifecycle-default';
  }
  if (normalized.startsWith('active')) {
    return 'lifecycle-active';
  }
  if (normalized.includes('liq')) {
    return 'lifecycle-liquidated';
  }
  if (normalized.includes('hold') || normalized.includes('watch')) {
    return 'lifecycle-hold';
  }
  return 'lifecycle-default';
}

// ============================================================================
// 🏷️ FLAG BADGE TONE HELPERS
// ============================================================================

/**
 * Foreclosure flag badge tone helper
 * @param flag - Boolean-ish value
 * @returns Badge tone key
 */
export function getFcFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'danger';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

/**
 * Bankruptcy flag badge tone helper
 * @param flag - Boolean-ish value
 * @returns Badge tone key
 */
export function getBkFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'danger';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

/**
 * Modification flag badge tone helper
 * @param flag - Boolean-ish value
 * @returns Badge tone key
 */
export function getModFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'info';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

// ============================================================================
// 📊 AG GRID ENUM MAPS - Auto-generated from category color configs
// ============================================================================

/**
 * Generate Property Type enum map for AG Grid
 * @returns Record with label, color (inline style), and title
 */
export function getPropertyTypeEnumMap(): Record<string, { label: string; color: string; title: string }> {
  const enumMap: Record<string, { label: string; color: string; title: string }> = {};

  for (const [key, tagColor] of Object.entries(PROPERTY_TYPE_COLORS)) {
    enumMap[key] = {
      label: key,
      color: `background-color: ${getTagColor(tagColor)};`,
      title: getPropertyTypeTitle(key),
    };
  }

  return enumMap;
}

/**
 * Generate Asset Master Status enum map for AG Grid
 * @returns Record with label, color (inline style), and title
 */
export function getAssetMasterStatusEnumMap(): Record<string, { label: string; color: string; title: string }> {
  const enumMap: Record<string, { label: string; color: string; title: string }> = {};

  for (const [key, tagColor] of Object.entries(ASSET_MASTER_STATUS_COLORS)) {
    enumMap[key] = {
      label: key === 'ACTIVE' ? 'Active' : 'Liquidated',
      color: `background-color: ${getTagColor(tagColor)};`,
      title: key === 'ACTIVE' ? 'Active Asset Status' : 'Liquidated Asset Status',
    };
  }

  return enumMap;
}

/**
 * Generate Loan Performance enum map for AG Grid
 * @returns Record with label, color (inline style), and title
 */
export function getLoanPerformanceEnumMap(): Record<string, { label: string; color: string; title: string }> {
  const enumMap: Record<string, { label: string; color: string; title: string }> = {};

  for (const [key, tagColor] of Object.entries(LOAN_PERFORMANCE_COLORS)) {
    enumMap[key] = {
      label: key === 'PERFORMING' ? 'PERF' : key,
      color: `background-color: ${getTagColor(tagColor)};`,
      title: getLoanPerformanceTitle(key),
    };
  }

  return enumMap;
}

/**
 * Generate Asset Pipeline Track enum map for AG Grid
 * @returns Record with label, color (inline style), and title
 */
export function getAssetPipelineTrackEnumMap(): Record<string, { label: string; color: string; title: string }> {
  const enumMap: Record<string, { label: string; color: string; title: string }> = {};

  for (const [key, tagColor] of Object.entries(ASSET_PIPELINE_TRACK_COLORS)) {
    enumMap[key] = {
      label: key,
      color: `background-color: ${getTagColor(tagColor)};`,
      title: getAssetPipelineTrackTitle(key),
    };
  }

  return enumMap;
}

/**
 * Generate Asset Pipeline Track color map (for activeTasksColorMap)
 * @returns Record with color (inline style) strings
 */
export function getAssetPipelineTrackColorMap(): Record<string, string> {
  const colorMap: Record<string, string> = {};

  for (const [key, tagColor] of Object.entries(ASSET_PIPELINE_TRACK_COLORS)) {
    colorMap[key] = `background-color: ${getTagColor(tagColor)};`;
  }

  return colorMap;
}

// ============================================================================
// 📊 PREDEFINED ENUM MAPS FOR COMMON USE CASES
// ============================================================================

/**
 * AG Grid enum map for Property Type badges
 */
export const propertyTypeEnumMap: Record<string, { label: string; color: string; title: string }> = getPropertyTypeEnumMap();

/**
 * AG Grid enum map for Occupancy badges
 */
export const occupancyEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'Vacant': { label: 'Vacant', color: 'bg-danger', title: 'Property is Vacant' },
  'Occupied': { label: 'Occupied', color: 'bg-success', title: 'Property is Occupied' },
  'Unknown': { label: 'Occ. Unknown', color: 'bg-warning text-white', title: 'Occupancy Status Unknown' },
  'Owner Occupied': { label: 'Owner Occupied', color: 'bg-primary', title: 'Owner Occupied' },
  'Non-Owner Occupied': { label: 'Non-Owner Occupied', color: 'bg-info', title: 'Non-Owner Occupied' },
  'Investment': { label: 'Investment', color: 'bg-warning text-white', title: 'Investment Property' },
};

/**
 * AG Grid enum map for Asset Status badges (Loan Performance)
 */
export const assetStatusEnumMap: Record<string, { label: string; color: string; title: string }> = getLoanPerformanceEnumMap();

/**
 * AG Grid enum map for Product Type badges
 */
export const productTypeEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'BPL': { label: 'BPL', color: 'bg-primary', title: 'Business Purpose Loan' },
  'FRM': { label: 'FRM', color: 'bg-success', title: 'Fixed Rate Mortgage' },
  'ARM': { label: 'ARM', color: 'bg-info', title: 'Adjustable Rate Mortgage' },
  'HELOC': { label: 'HELOC', color: 'bg-warning text-white', title: 'Home Equity Line of Credit' },
  'Other': { label: 'Other', color: 'bg-secondary', title: 'Other Product Type' },
};

/**
 * AG Grid enum map for Active Tracks (outcome workflows)
 */
export const activeTracksEnumMap: Record<string, { label: string; color: string; title: string }> = getAssetPipelineTrackEnumMap();

/**
 * Color map for Active Tracks badges (used in AG Grid)
 */
export const activeTasksColorMap: Record<string, string> = getAssetPipelineTrackColorMap();

/**
 * AG Grid enum maps for FC/BK/Mod flags
 */
export const foreclosureFlagEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'Yes': { label: 'Yes', color: 'bg-danger text-white', title: 'Foreclosure Flag' },
  'No': { label: 'No', color: 'bg-secondary text-white', title: 'Foreclosure Flag' },
  '—': { label: '—', color: 'bg-secondary text-white', title: 'Foreclosure Flag' },
};

export const bankruptcyFlagEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'Yes': { label: 'Yes', color: 'bg-danger text-white', title: 'Bankruptcy Flag' },
  'No': { label: 'No', color: 'bg-secondary text-white', title: 'Bankruptcy Flag' },
  '—': { label: '—', color: 'bg-secondary text-white', title: 'Bankruptcy Flag' },
};

export const modificationFlagEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'Yes': { label: 'Yes', color: 'bg-info text-white', title: 'Modification Flag' },
  'No': { label: 'No', color: 'bg-secondary text-white', title: 'Modification Flag' },
  '—': { label: '—', color: 'bg-secondary text-white', title: 'Modification Flag' },
};

// ============================================================================
// 🔧 INTERNAL TITLE HELPERS
// ============================================================================

function getPropertyTypeTitle(key: string): string {
  const titles: Record<string, string> = {
    'SFR': 'Single Family Residence',
    'Single Family': 'Single Family Residence',
    'Manufactured': 'Manufactured Home',
    'Condo': 'Condominium',
    'Townhouse': 'Townhouse',
    '2-4 Family': '2-4 Family Property',
    'Multifamily 5+': 'Multifamily 5+ Units',
    'Multi-Family': 'Multi-Family Property',
    'Land': 'Vacant Land',
  };
  return titles[key] || key;
}

function getLoanPerformanceTitle(key: string): string {
  const titles: Record<string, string> = {
    'NPL': 'Non-Performing Loan',
    'REO': 'Real Estate Owned',
    'PERF': 'Performing',
    'PERFORMING': 'Performing',
    'RPL': 'Re-Performing Loan',
  };
  return titles[key] || key;
}

function getAssetPipelineTrackTitle(key: string): string {
  const titles: Record<string, string> = {
    'DIL': 'Deed in Lieu',
    'Modification': 'Loan Modification',
    'REO': 'Real Estate Owned',
    'FC': 'Foreclosure Sale',
    'Short Sale': 'Short Sale',
    'Note Sale': 'Note Sale',
    'Performing': 'Performing Track',
    'Delinquent': 'Delinquent Track',
  };
  return titles[key] || key;
}
