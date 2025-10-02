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
 */
export const propertyTypeToneLookup: Record<string, BadgeToneKey> = {
  sfr: 'property-sfr',
  manufactured: 'property-sfr',
  condo: 'property-condo',
  '2-4 family': 'property-multifamily',
  land: 'property-land',
  'multifamily 5+': 'property-multifamily',
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
