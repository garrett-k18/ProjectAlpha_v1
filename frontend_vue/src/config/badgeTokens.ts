/**
 * GARRETT...CONTROL BADGE SETTINGS HERE DUMBASS
 * 
 * ============================================================================
 * BADGE TOKENS - SINGLE SOURCE OF TRUTH FOR ALL BADGE STYLING
 * ============================================================================
 * 
 * WHAT: Complete badge configuration system with styling variables and mappings
 * WHY: Eliminates dual styling sources and provides easy maintenance
 * HOW: Centralized variables + mappings + helper functions
 * 
 * Documentation: https://hyperui.dev/components/badges
 * ============================================================================
 */

// ============================================================================
// 🎨 MASTER STYLING VARIABLES - EDIT THESE TO CHANGE ALL BADGE DIMENSIONS
// ============================================================================

/**
 * Master pill dimensions - Change these values to adjust all badge sizes globally
 */
const PILL_DIMENSIONS = {
  xs: {
    paddingX: '0.5rem',    // px-2 equivalent
    paddingY: '0.125rem',  // Tight vertical padding
    fontSize: '0.5rem',    // Very small text
    borderRadius: '9999px' // Full rounded pill
  },
  sm: {
    paddingX: '0.5rem',    // px-2 equivalent  
    paddingY: '0.2rem',    // Current production padding
    fontSize: '0.7rem',    // Current production font size
    borderRadius: '9999px' // Full rounded pill
  },
  md: {
    paddingX: '0.75rem',   // px-3 equivalent
    paddingY: '0.25rem',   // Medium padding
    fontSize: '0.75rem',   // Medium font size
    borderRadius: '9999px' // Full rounded pill
  },
  lg: {
    paddingX: '1rem',      // px-4 equivalent
    paddingY: '0.375rem',  // Large padding
    fontSize: '0.875rem',  // Large font size
    borderRadius: '9999px' // Full rounded pill
  }
} as const;

// ============================================================================
// 🏗️ TYPE DEFINITIONS
// ============================================================================

/**
 * Badge size type definition
 */
export type BadgeSizeKey = keyof typeof PILL_DIMENSIONS;

export interface BadgeVisualConfig {
  /** Tailwind/Bootstrap classes for styling */
  classes: string;
  /** Optional ARIA label for accessibility */
  ariaLabel?: string;
  /** Inline CSS styles for precise control */
  inlineStyles?: string;
}

// ============================================================================
// 🎨 COLOR TONE DEFINITIONS - Add/Remove badge colors here
// ============================================================================

export type BadgeToneKey =
  // Standard Bootstrap colors
  | 'primary'
  | 'secondary'
  | 'dark'
  | 'info'
  | 'success'
  | 'warning'
  | 'danger'
  // Track-specific colors
  | 'modification-green'
  // Delinquency-specific colors
  | 'delinquency-current'
  | 'delinquency-30'
  | 'delinquency-60'
  | 'delinquency-90'
  | 'delinquency-120-plus'
  // Property type colors
  | 'property-sfr'
  | 'property-condo'
  | 'property-townhome'
  | 'property-multifamily'
  | 'property-land'
  | 'property-mixed-use'
  | 'property-other';

// ============================================================================
// 📏 SIZE CONFIGURATIONS - Uses master variables above
// ============================================================================

/**
 * Badge size configurations built from master PILL_DIMENSIONS
 * EDIT PILL_DIMENSIONS above to change all badge sizes globally
 */
export const badgeSizeMap: Record<BadgeSizeKey, BadgeVisualConfig> = {
  xs: {
    classes: 'badge rounded-pill fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.xs.paddingY} ${PILL_DIMENSIONS.xs.paddingX}; font-size: ${PILL_DIMENSIONS.xs.fontSize}; border-radius: ${PILL_DIMENSIONS.xs.borderRadius};`,
  },
  sm: {
    classes: 'badge rounded-pill fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.sm.paddingY} ${PILL_DIMENSIONS.sm.paddingX}; font-size: ${PILL_DIMENSIONS.sm.fontSize}; border-radius: ${PILL_DIMENSIONS.sm.borderRadius};`,
  },
  md: {
    classes: 'badge rounded-pill fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.md.paddingY} ${PILL_DIMENSIONS.md.paddingX}; font-size: ${PILL_DIMENSIONS.md.fontSize}; border-radius: ${PILL_DIMENSIONS.md.borderRadius};`,
  },
  lg: {
    classes: 'badge rounded-pill fw-bold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.lg.paddingY} ${PILL_DIMENSIONS.lg.paddingX}; font-size: ${PILL_DIMENSIONS.lg.fontSize}; border-radius: ${PILL_DIMENSIONS.lg.borderRadius};`,
  },
};

// ============================================================================
// 🌈 COLOR MAPPINGS - Edit these to change badge colors
// ============================================================================

/**
 * Badge color configurations - Add/edit colors here
 * Uses Bootstrap/Hyper UI color classes
 */
export const badgeToneMap: Record<BadgeToneKey, BadgeVisualConfig> = {
  // Standard Bootstrap Colors
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
  
  // Track-specific Colors
  'modification-green': {
    classes: 'bg-success text-white border-0',
    ariaLabel: undefined,
  },
  
  // Delinquency Status Colors
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

  // Property Type Colors
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
};

// ============================================================================
// 🔧 CORE HELPER FUNCTIONS
// ============================================================================

export interface BadgeTokenLookupResult {
  /** Computed class string after merging size + tone. */
  classes: string;
  /** Optional aria label we surfaced from tone config. */
  ariaLabel?: string;
  /** Optional inline styles for precise control. */
  inlineStyles?: string;
}

/**
 * SINGLE SOURCE OF TRUTH: Helper to merge tone and size definitions.
 * WHAT: Combines size + tone configs into complete badge styling
 * WHY: Eliminates need for dual styling in component files
 * HOW: Merges classes and passes through inline styles from size config
 */
export function resolveBadgeTokens(
  toneKey: BadgeToneKey,
  sizeKey: BadgeSizeKey = 'md',
): BadgeTokenLookupResult {
  const tone = badgeToneMap[toneKey];
  const size = badgeSizeMap[sizeKey];

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
// 🗺️ FIELD VALUE MAPPINGS - Add/edit field-to-badge mappings here
// ============================================================================

/**
 * Map occupancy values to badge tones.
 * EDIT: Add new occupancy values here
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
 * EDIT: Add new asset status values here
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
 * EDIT: Add new product types here
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
 * Normalized lookup for property type strings to badge tone keys.
 * EDIT: Add new property type variations here
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
 * EDIT: Modify logic here if needed
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
 * EDIT: Add new delinquency statuses here
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

// ============================================================================
// 📊 AG GRID ENUM MAPS - For AG Grid badge cell renderers
// ============================================================================

/**
 * AG Grid enum map for Property Type badges
 * EDIT: Add new property types for AG Grid here
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
 * EDIT: Add new occupancy statuses for AG Grid here
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
 * EDIT: Add new asset statuses for AG Grid here
 */
export const assetStatusEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'NPL': { label: 'NPL', color: 'bg-danger', title: 'Non-Performing Loan' },
  'REO': { label: 'REO', color: 'bg-secondary', title: 'Real Estate Owned' },
  'PERF': { label: 'PERF', color: 'bg-success', title: 'Performing' },
  'RPL': { label: 'RPL', color: 'bg-info', title: 'Re-Performing Loan' },
};

/**
 * AG Grid enum map for Product Type badges
 * EDIT: Add new product types for AG Grid here
 */
export const productTypeEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'BPL': { label: 'BPL', color: 'bg-primary', title: 'Business Purpose Loan' },
  'FRM': { label: 'FRM', color: 'bg-success', title: 'Fixed Rate Mortgage' },
  'ARM': { label: 'ARM', color: 'bg-info', title: 'Adjustable Rate Mortgage' },
  'HELOC': { label: 'HELOC', color: 'bg-warning text-dark', title: 'Home Equity Line of Credit' },
  'Other': { label: 'Other', color: 'bg-secondary', title: 'Other Product Type' },
};

// ============================================================================
// 🔧 UTILITY FUNCTIONS
// ============================================================================

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
 * EDIT: Modify flag color logic here
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
 * EDIT: Modify flag display here
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
