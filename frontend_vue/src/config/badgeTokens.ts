// Hyper UI badge config tokens
// Documentation consulted: https://hyperui.dev/components/badges
// This module centralizes *design system data* only (sizes, tones, accessibility labels) so
// Vue components, stores, or even non-Vue utilities can consume the same palette without
// duplicating class strings. Rendering logic lives in `components/ui/UiBadge.vue`; this file
// remains framework-agnostic to keep badge styling reusable across the project.

export type BadgeSizeKey = 'xs' | 'sm' | 'md' | 'lg';

export interface BadgeVisualConfig {
  /**
   * Tailwind/Hyper UI class string that controls the pill background, text color, padding, and font treatment.
   * Keeping this centralized avoids style drift across the platform.
   */
  classes: string;

  /**
   * Optional ARIA label override. Useful when we want screen readers to spell out abbreviations like "30D".
   */
  ariaLabel?: string;
}

/**
 * Map occupancy values to badge tones.
 */
export function getOccupancyBadgeTone(occupancy?: string | null): BadgeToneKey {
  const v = (occupancy ?? '').toString().toLowerCase();
  if (v === 'occupied') return 'success';
  if (v === 'vacant') return 'danger';
  if (v === 'unknown') return 'warning';
  return 'secondary';
}

/**
 * Map asset status (NPL/REO/PERF/RPL) to badge tones.
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
 * Map product type strings to badge tones.
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
 * Shared size presets. Combine with `badgeToneMap` entries to create consistent pills.
 */
export const badgeSizeMap: Record<BadgeSizeKey, BadgeVisualConfig> = {
  xs: {
    classes: 'badge rounded-pill px-2 py-0.5 text-xs fw-semibold',
    ariaLabel: undefined,
  },
  sm: {
    classes: 'badge rounded-pill px-2.5 py-1 text-sm fw-semibold',
    ariaLabel: undefined,
  },
  md: {
    classes: 'badge rounded-pill px-3 text-base fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
  },
  lg: {
    classes: 'badge rounded-pill px-4 py-1.5 text-lg fw-bold',
    ariaLabel: undefined,
  },
};

export type BadgeToneKey =
  | 'delinquency-current'
  | 'delinquency-30'
  | 'delinquency-60'
  | 'delinquency-90'
  | 'delinquency-120-plus'
  | 'property-sfr'
  | 'property-condo'
  | 'property-townhome'
  | 'property-multifamily'
  | 'property-land'
  | 'property-mixed-use'
  | 'property-other'
  | 'primary'
  | 'secondary'
  | 'dark'
  | 'info'
  | 'success'
  | 'warning'
  | 'danger';

/**
 * Tone palette for badges. These align to Hyper UI badge color recommendations.
 */
export const badgeToneMap: Record<BadgeToneKey, BadgeVisualConfig> = {
  primary: {
    classes: 'bg-primary text-white border-0',
    ariaLabel: undefined,
  },
  secondary: {
    classes: 'bg-secondary text-white border-0',
    ariaLabel: undefined,
  },
  dark: {
    classes: 'bg-dark text-white border-0',
    ariaLabel: undefined,
  },
  'delinquency-current': {
    classes: 'bg-success text-white border-0 shadow-sm',
    ariaLabel: 'Current delinquency status',
  },
  'delinquency-30': {
    classes: 'bg-warning text-dark border-0 shadow-sm',
    ariaLabel: 'Thirty days delinquent',
  },
  'delinquency-60': {
    classes: 'bg-warning text-dark border-0 shadow-sm',
    ariaLabel: 'Sixty days delinquent',
  },
  'delinquency-90': {
    classes: 'bg-danger text-white border-0 shadow-sm',
    ariaLabel: 'Ninety days delinquent',
  },
  'delinquency-120-plus': {
    classes: 'bg-danger text-white border-0 shadow',
    ariaLabel: 'Delinquent one hundred twenty days or more',
  },
  'property-sfr': {
    classes: 'bg-primary text-white border-0',
    ariaLabel: 'Single family residence property type',
  },
  'property-condo': {
    classes: 'bg-info text-white border-0',
    ariaLabel: 'Condominium property type',
  },
  'property-townhome': {
    classes: 'bg-secondary text-white border-0',
    ariaLabel: 'Townhome property type',
  },
  'property-multifamily': {
    classes: 'bg-success text-white border-0',
    ariaLabel: 'Multifamily property type',
  },
  'property-land': {
    classes: 'bg-warning text-dark border-0',
    ariaLabel: 'Land property type',
  },
  'property-mixed-use': {
    classes: 'bg-purple text-white border-0',
    ariaLabel: 'Mixed use property type',
  },
  'property-other': {
    classes: 'bg-dark text-white border-0',
    ariaLabel: 'Other property type classification',
  },
  info: {
    classes: 'bg-info text-white border-0',
    ariaLabel: undefined,
  },
  success: {
    classes: 'bg-success text-white border-0',
    ariaLabel: undefined,
  },
  warning: {
    classes: 'bg-warning text-dark border-0',
    ariaLabel: undefined,
  },
  danger: {
    classes: 'bg-danger text-white border-0',
    ariaLabel: undefined,
  },
};

export interface BadgeTokenLookupResult {
  /** Computed class string after merging size + tone. */
  classes: string;
  /** Optional aria label we surfaced from tone config. */
  ariaLabel?: string;
}

/**
 * Helper to merge tone and size definitions.
 */
export function resolveBadgeTokens(
  toneKey: BadgeToneKey,
  sizeKey: BadgeSizeKey = 'md',
): BadgeTokenLookupResult {
  const tone = badgeToneMap[toneKey];
  const size = badgeSizeMap[sizeKey];

  return {
    classes: `${size.classes} ${tone.classes}`.trim(),
    ariaLabel: tone.ariaLabel ?? size.ariaLabel,
  };
}

/**
 * Normalized lookup for property type strings to badge tone keys.
 * WHAT: Maps all property type variations to consistent badge colors
 * WHY: Different sellers use different naming conventions
 * HOW: Lowercase normalized keys map to predefined tone keys
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
 * Helper that resolves a property type string to an appropriate badge tone key.
 */
export function getPropertyTypeBadgeTone(propertyType?: string | null): BadgeToneKey {
  if (!propertyType) {
    return 'property-other';
  }
  const normalized = propertyType.trim().toLowerCase();
  return propertyTypeToneLookup[normalized] ?? 'property-other';
}

/**
 * Helper that maps delinquency buckets to badge tone keys.
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
 * AG Grid enum map for Property Type badges
 * WHAT: Centralized property type badge configuration for AG Grid
 * WHY: Keeps badge styling consistent across all grids
 * HOW: Maps property type values to label, color, and title
 */
export const propertyTypeEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'SFR': { label: 'SFR', color: 'bg-primary', title: 'Single Family Residence' },
  'Manufactured': { label: 'Manufactured', color: 'bg-primary', title: 'Manufactured Home' },
  'Condo': { label: 'Condo', color: 'bg-info', title: 'Condominium' },
  '2-4 Family': { label: '2-4 Family', color: 'bg-success', title: '2-4 Family Property' },
  'Land': { label: 'Land', color: 'bg-warning text-dark', title: 'Vacant Land' },
  'Multifamily 5+': { label: 'Multifamily 5+', color: 'bg-success', title: 'Multifamily 5+ Units' },
  'Single Family': { label: 'Single Family', color: 'bg-primary', title: 'Single Family Residence' },
  'Multi-Family': { label: 'Multi-Family', color: 'bg-success', title: 'Multi-Family Property' },
  'Townhouse': { label: 'Townhouse', color: 'bg-secondary', title: 'Townhouse' },
};

/**
 * AG Grid enum map for Occupancy badges
 * WHAT: Centralized occupancy badge configuration for AG Grid
 * WHY: Keeps badge styling consistent across all grids
 * HOW: Maps occupancy values to label, color, and title
 */
export const occupancyEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'Vacant': { label: 'Vacant', color: 'bg-danger', title: 'Property is Vacant' },
  'Occupied': { label: 'Occupied', color: 'bg-success', title: 'Property is Occupied' },
  'Unknown': { label: 'Occ. Unknown', color: 'bg-warning text-dark', title: 'Occupancy Status Unknown' },
  'Owner Occupied': { label: 'Owner Occupied', color: 'bg-primary', title: 'Owner Occupied' },
  'Non-Owner Occupied': { label: 'Non-Owner Occupied', color: 'bg-info', title: 'Non-Owner Occupied' },
  'Investment': { label: 'Investment', color: 'bg-warning text-dark', title: 'Investment Property' },
};

/**
 * AG Grid enum map for Asset Status badges
 * WHAT: Centralized asset status badge configuration for AG Grid
 * WHY: Keeps badge styling consistent across all grids
 * HOW: Maps asset status values to label, color, and title
 */
export const assetStatusEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'NPL': { label: 'NPL', color: 'bg-danger', title: 'Non-Performing Loan' },
  'REO': { label: 'REO', color: 'bg-secondary', title: 'Real Estate Owned' },
  'PERF': { label: 'PERF', color: 'bg-success', title: 'Performing' },
  'RPL': { label: 'RPL', color: 'bg-info', title: 'Re-Performing Loan' },
};

/**
 * AG Grid enum map for Product Type badges
 * WHAT: Centralized product type badge configuration for AG Grid
 * WHY: Keeps badge styling consistent across all grids
 * HOW: Maps product type values to label, color, and title
 */
export const productTypeEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'BPL': { label: 'BPL', color: 'bg-primary', title: 'Business Purpose Loan' },
  'FRM': { label: 'FRM', color: 'bg-success', title: 'Fixed Rate Mortgage' },
  'ARM': { label: 'ARM', color: 'bg-info', title: 'Adjustable Rate Mortgage' },
  'HELOC': { label: 'HELOC', color: 'bg-warning text-dark', title: 'Home Equity Line of Credit' },
  'Other': { label: 'Other', color: 'bg-secondary', title: 'Other Product Type' },
};

/**
 * Utility: normalize various boolean-ish values into Yes/No/— labels.
 */
export function toYesNoLabel(v: any): string {
  if (v === true || v === 'true' || v === 'True' || v === 'YES' || v === 'Yes' || v === 'Y' || v === 1) return 'Yes';
  if (v === false || v === 'false' || v === 'False' || v === 'NO' || v === 'No' || v === 'N' || v === 0) return 'No';
  return '—';
}

/**
 * Flag badge tone helpers (standardize FC/BK/Mod visuals across app).
 * Aligns with AG Grid-like red for risk flags, green for clear, info for mod present.
 */
export function getFcFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'danger';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

export function getBkFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'danger';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

export function getModFlagBadgeTone(flag?: any): BadgeToneKey {
  const lbl = toYesNoLabel(flag);
  if (lbl === 'Yes') return 'info';
  if (lbl === 'No') return 'secondary';
  return 'secondary';
}

/**
 * AG Grid enum maps for FC/BK/Mod flags to keep grid pills consistent with components.
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
