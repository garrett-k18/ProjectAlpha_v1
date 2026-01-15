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
 * ⚠️ IMPORTANT COLOR RULES:
 * ========================
 * 1. ALL COLORS MUST COME FROM colorPalette.ts
 * 2. DO NOT use hardcoded hex values (e.g., '#FF0000')
 * 3. Use STATUS_COLORS or TAG_COLORS constants
 * 4. Use helper functions: getStatusColor(), getTagColor(), createPaletteBadge()
 * 
 * ✅ CORRECT Examples:
 * - inlineStyles: `background-color: ${STATUS_COLORS.success};`
 * - inlineStyles: `background-color: ${getTagColor('clay')};`
 * - createPaletteBadge(STATUS_COLORS.warning, 'My badge')
 * 
 * ❌ WRONG Examples:
 * - inlineStyles: 'background-color: #FF0000;'  // Hardcoded hex
 * - inlineStyles: 'background-color: red;'      // Color name
 * 
 * Documentation: https://hyperui.dev/components/badges
 * ============================================================================
 */

import {
  STATUS_COLORS,
  TAG_COLORS,
  getStatusColor,
  getTagColor,
  COLOR_INFO_TEAL,
  COLOR_MUTED_PLUM,
  COLOR_STEEL_TEAL,
  COLOR_SLATE_TEAL,
  COLOR_INDIGO,
  COLOR_DUSTY_LAVENDER,
} from './colorPalette';
import {
  getPropertyTypeEnumMap,
  getAssetMasterStatusEnumMap,
  getLoanPerformanceEnumMap,
  getAssetPipelineTrackEnumMap,
  getAssetPipelineTrackColorMap,
} from './categoryColors';

// ============================================================================
// 🎨 MASTER STYLING VARIABLES - EDIT THESE TO CHANGE ALL BADGE DIMENSIONS
// ============================================================================

/**
 * Master badge dimensions - Change these values to adjust all badge sizes globally
 * UPDATED: Changed from rounded pills to square badges for more professional/serious tone
 */
const PILL_DIMENSIONS = {
  xs: {
    paddingX: '0.5rem',    // px-2 equivalent
    paddingY: '0.125rem',  // Tight vertical padding
    fontSize: '0.5rem',    // Very small text
    borderRadius: '0.25rem' // Slightly rounded square (more professional)
  },
  sm: {
    paddingX: '0.5rem',    // px-2 equivalent  
    paddingY: '0.2rem',    // Current production padding
    fontSize: '0.7rem',    // Current production font size
    borderRadius: '0.25rem' // Slightly rounded square (more professional)
  },
  md: {
    paddingX: '0.75rem',   // px-3 equivalent
    paddingY: '0.25rem',   // Medium padding
    fontSize: '0.75rem',   // Medium font size
    borderRadius: '0.25rem' // Slightly rounded square (more professional)
  },
  lg: {
    paddingX: '1rem',      // px-4 equivalent
    paddingY: '0.375rem',  // Large padding
    fontSize: '0.875rem',  // Large font size
    borderRadius: '0.375rem' // Slightly rounded square (more professional)
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
// IMPORTANT: All colors must come from colorPalette.ts
// Use STATUS_COLORS or TAG_COLORS constants - NO hardcoded hex values!

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
  // Calendar event type colors
  | 'calendar-liquidation'
  | 'calendar-projected'
  | 'calendar-bid'
  | 'calendar-settlement'
  | 'calendar-follow-up'
  | 'calendar-milestone'
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
  // Tag/Category colors (from SCSS palette)
  | 'tag-clay'
  | 'tag-thyme'
  | 'tag-stone'
  | 'tag-eucalyptus'
  | 'tag-seafoam'
  | 'tag-moss'
  | 'tag-mineral-blue'
  | 'tag-umber'
  | 'tag-mauve'
  | 'tag-heather'
  | 'tag-slate-purple'
  | 'tag-pewter'
  | 'tag-graphite'
  | 'tag-ash'
  | 'tag-navy-blue'
  | 'tag-info-blue'
  | 'tag-steel-gray'
  | 'property-multifamily'
  | 'property-land'
  | 'property-mixed-use'
  | 'property-other'
  // Lifecycle colors
  | 'lifecycle-active'
  | 'lifecycle-liquidated'
  | 'lifecycle-hold'
  | 'lifecycle-default';

// ============================================================================
// 📏 SIZE CONFIGURATIONS - Uses master variables above
// ============================================================================

/**
 * Badge size configurations built from master PILL_DIMENSIONS
 * EDIT PILL_DIMENSIONS above to change all badge sizes globally
 * UPDATED: Changed from rounded-pill to rounded for square badge style
 */
export const badgeSizeMap: Record<BadgeSizeKey, BadgeVisualConfig> = {
  xs: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.xs.paddingY} ${PILL_DIMENSIONS.xs.paddingX}; font-size: ${PILL_DIMENSIONS.xs.fontSize}; border-radius: ${PILL_DIMENSIONS.xs.borderRadius};`,
  },
  sm: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.sm.paddingY} ${PILL_DIMENSIONS.sm.paddingX}; font-size: ${PILL_DIMENSIONS.sm.fontSize}; border-radius: ${PILL_DIMENSIONS.sm.borderRadius};`,
  },
  md: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${PILL_DIMENSIONS.md.paddingY} ${PILL_DIMENSIONS.md.paddingX}; font-size: ${PILL_DIMENSIONS.md.fontSize}; border-radius: ${PILL_DIMENSIONS.md.borderRadius};`,
  },
  lg: {
    classes: 'badge rounded fw-bold d-inline-flex align-items-center justify-content-center',
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
    classes: 'bg-warning text-white border-0',
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
  
  // Calendar Event Type Colors
  // WHAT: Distinct colors for each calendar event type using ProjectAlpha palette
  // WHY: Users need to quickly identify different event types at a glance
  // NOTE: All colors from STATUS_COLORS - no hardcoded values
  'calendar-liquidation': {
    classes: 'text-white border-0',
    ariaLabel: 'Actual liquidation event',
    inlineStyles: `background-color: ${COLOR_INFO_TEAL};`, // Info Teal from palette
  },
  'calendar-projected': {
    classes: 'text-white border-0',
    ariaLabel: 'Projected liquidation event',
    inlineStyles: `background-color: ${COLOR_MUTED_PLUM};`, // Muted Plum from palette
  },
  'calendar-bid': {
    classes: 'text-white border-0',
    ariaLabel: 'Bid date event',
    inlineStyles: `background-color: ${COLOR_STEEL_TEAL};`, // Steel Teal from palette
  },
  'calendar-settlement': {
    classes: 'text-white border-0',
    ariaLabel: 'Settlement date event',
    inlineStyles: `background-color: ${COLOR_SLATE_TEAL};`, // Slate Teal from palette
  },
  'calendar-follow-up': {
    classes: 'text-white border-0',
    ariaLabel: 'Follow-up reminder event',
    inlineStyles: `background-color: ${COLOR_INDIGO};`, // Indigo from palette
  },
  'calendar-milestone': {
    classes: 'text-white border-0',
    ariaLabel: 'Milestone event',
    inlineStyles: `background-color: ${COLOR_DUSTY_LAVENDER};`, // Dusty Lavender from palette
  },
  
  // Delinquency Status Colors
  'delinquency-current': {
    classes: 'bg-success text-white border-0 shadow-sm',
    ariaLabel: 'Current delinquency status',
  },
  'delinquency-30': {
    classes: 'bg-warning text-white border-0 shadow-sm',
    ariaLabel: 'Thirty days delinquent',
  },
  'delinquency-60': {
    classes: 'bg-warning text-white border-0 shadow-sm',
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

  // Property Type Colors (using tag colors from palette)
  'property-sfr': {
    classes: 'text-white border-0',
    ariaLabel: 'Single family residence property type',
    inlineStyles: `background-color: ${getTagColor('navy-blue')};`,
  },
  'property-condo': {
    classes: 'text-white border-0',
    ariaLabel: 'Condominium property type',
    inlineStyles: `background-color: ${getTagColor('info-blue')};`,
  },
  'property-townhome': {
    classes: 'text-white border-0',
    ariaLabel: 'Townhome property type',
    inlineStyles: `background-color: ${getTagColor('steel-gray')};`,
  },
  'property-multifamily': {
    classes: 'bg-success text-white border-0',
    ariaLabel: 'Multifamily property type',
  },
  'property-land': {
    classes: 'bg-warning text-white border-0',
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

  // Lifecycle status colors
  'lifecycle-active': {
    classes: 'bg-success text-white border-0',
    ariaLabel: 'Active lifecycle status',
  },
  'lifecycle-liquidated': {
    classes: 'bg-secondary text-white border-0',
    ariaLabel: 'Liquidated lifecycle status',
  },
  'lifecycle-hold': {
    classes: 'bg-warning text-white border-0',
    ariaLabel: 'Hold or watch lifecycle status',
  },
  'lifecycle-default': {
    classes: 'bg-dark text-white border-0',
    ariaLabel: 'Lifecycle status',
  },
  
  // ============================================================================
  // 🏷️ TAG/CATEGORY COLORS - From colorPalette.ts (mirrors SCSS palette)
  // ============================================================================
  // Main Tags (Primary Classifications)
  'tag-clay': {
    classes: 'text-white border-0',
    ariaLabel: 'Document or property classification tag',
    inlineStyles: `background-color: ${getTagColor('clay')};`,
  },
  'tag-thyme': {
    classes: 'text-white border-0',
    ariaLabel: 'Property type classification tag',
    inlineStyles: `background-color: ${getTagColor('thyme')};`,
  },
  'tag-stone': {
    classes: 'text-white border-0',
    ariaLabel: 'General classification tag',
    inlineStyles: `background-color: ${getTagColor('stone')};`,
  },
  'tag-eucalyptus': {
    classes: 'text-white border-0',
    ariaLabel: 'Positive feature or attribute tag',
    inlineStyles: `background-color: ${getTagColor('eucalyptus')};`,
  },
  'tag-seafoam': {
    classes: 'text-white border-0',
    ariaLabel: 'Location or geographic tag',
    inlineStyles: `background-color: ${getTagColor('seafoam')};`,
  },
  'tag-moss': {
    classes: 'text-white border-0',
    ariaLabel: 'Environmental or nature tag',
    inlineStyles: `background-color: ${getTagColor('moss')};`,
  },
  'tag-mineral-blue': {
    classes: 'text-white border-0',
    ariaLabel: 'Reference or information tag',
    inlineStyles: `background-color: ${getTagColor('mineral-blue')};`,
  },
  'tag-umber': {
    classes: 'text-white border-0',
    ariaLabel: 'Foundation or structural tag',
    inlineStyles: `background-color: ${getTagColor('umber')};`,
  },
  
  // Sub-Tags (Secondary/Supporting)
  'tag-mauve': {
    classes: 'text-white border-0',
    ariaLabel: 'Workflow or review state tag',
    inlineStyles: `background-color: ${getTagColor('mauve')};`,
  },
  'tag-heather': {
    classes: 'text-white border-0',
    ariaLabel: 'Process or workflow stage tag',
    inlineStyles: `background-color: ${getTagColor('heather')};`,
  },
  'tag-slate-purple': {
    classes: 'text-white border-0',
    ariaLabel: 'Advanced workflow or special process tag',
    inlineStyles: `background-color: ${getTagColor('slate-purple')};`,
  },
  'tag-pewter': {
    classes: 'text-white border-0',
    ariaLabel: 'Metadata or system tag',
    inlineStyles: `background-color: ${getTagColor('pewter')};`,
  },
  'tag-graphite': {
    classes: 'text-white border-0',
    ariaLabel: 'Secondary or supporting tag',
    inlineStyles: `background-color: ${getTagColor('graphite')};`,
  },
  'tag-ash': {
    classes: 'text-white border-0',
    ariaLabel: 'Archived or inactive tag',
    inlineStyles: `background-color: ${getTagColor('ash')};`,
  },
  
  // Blue Variants (Property Types & Classifications)
  'tag-navy-blue': {
    classes: 'text-white border-0',
    ariaLabel: 'Primary property type tag',
    inlineStyles: `background-color: ${getTagColor('navy-blue')};`,
  },
  'tag-info-blue': {
    classes: 'text-white border-0',
    ariaLabel: 'Informational property type tag',
    inlineStyles: `background-color: ${getTagColor('info-blue')};`,
  },
  'tag-steel-gray': {
    classes: 'text-white border-0',
    ariaLabel: 'Secondary property type tag',
    inlineStyles: `background-color: ${getTagColor('steel-gray')};`,
  },
};

// ============================================================================
// 🔧 CORE HELPER FUNCTIONS
// ============================================================================

/**
 * Helper to create badge config with palette color
 * ENFORCES: Only palette colors can be used - no random hex values
 * 
 * @param color - Palette color constant from colorPalette.ts
 * @param ariaLabel - Optional ARIA label for accessibility
 * @returns BadgeVisualConfig with inline styles using palette color
 * 
 * @example
 * // ✅ CORRECT - Uses palette color
 * 'my-workflow': createPaletteBadge(STATUS_COLORS.success, 'My workflow badge')
 * 
 * // ❌ WRONG - Don't do this
 * 'my-workflow': { inlineStyles: 'background-color: #FF0000;' }
 */
export function createPaletteBadge(
  color: string,
  ariaLabel?: string
): BadgeVisualConfig {
  return {
    classes: 'text-white border-0',
    ariaLabel,
    inlineStyles: `background-color: ${color};`,
  };
}

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
 * ⚠️ EDIT COLORS IN: categoryColors.ts → PROPERTY_TYPE_COLORS
 * This map is auto-generated from categoryColors.ts configuration
 */
export const propertyTypeEnumMap: Record<string, { label: string; color: string; title: string }> = getPropertyTypeEnumMap();

/**
 * AG Grid enum map for Occupancy badges
 * EDIT: Add new occupancy statuses for AG Grid here
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
 * ⚠️ EDIT COLORS IN: categoryColors.ts → LOAN_PERFORMANCE_COLORS
 * This map is auto-generated from categoryColors.ts configuration
 */
export const assetStatusEnumMap: Record<string, { label: string; color: string; title: string }> = getLoanPerformanceEnumMap();

/**
 * AG Grid enum map for Product Type badges
 * EDIT: Add new product types for AG Grid here
 */
export const productTypeEnumMap: Record<string, { label: string; color: string; title: string }> = {
  'BPL': { label: 'BPL', color: 'bg-primary', title: 'Business Purpose Loan' },
  'FRM': { label: 'FRM', color: 'bg-success', title: 'Fixed Rate Mortgage' },
  'ARM': { label: 'ARM', color: 'bg-info', title: 'Adjustable Rate Mortgage' },
  'HELOC': { label: 'HELOC', color: 'bg-warning text-white', title: 'Home Equity Line of Credit' },
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

/**
 * AG Grid enum map for Active Tracks (outcome workflows)
 * ⚠️ EDIT COLORS IN: categoryColors.ts → ASSET_PIPELINE_TRACK_COLORS
 * IMPORTANT: When adding a new backend track/task model, keep this list in sync with
 * `projectalphav1/am_module/services/serv_am_assetInventory.py` (active_tracks/active_tasks).
 * This map is auto-generated from categoryColors.ts configuration
 */
export const activeTracksEnumMap: Record<string, { label: string; color: string; title: string }> = getAssetPipelineTrackEnumMap();

/**
 * Color map for Active Tracks badges (used in AG Grid)
 * ⚠️ EDIT COLORS IN: categoryColors.ts → ASSET_PIPELINE_TRACK_COLORS
 * This map is auto-generated from categoryColors.ts configuration
 */
export const activeTasksColorMap: Record<string, string> = getAssetPipelineTrackColorMap();

/**
 * Helper that maps calendar event types to badge tone keys
 * EDIT: Add new calendar event types here
 */
export function getCalendarEventBadgeTone(eventType?: string | null): BadgeToneKey {
  switch ((eventType ?? '').toLowerCase()) {
    case 'actual_liquidation':
      return 'calendar-liquidation';
    case 'projected_liquidation':
      return 'calendar-projected';
    case 'bid_date':
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
 * Returns hex color values matching the saas theme from _variables.scss
 * Theme colors: primary=#1B3B5F, success=#2E7D32, info=#5A8A95, warning=#D4AF37, danger=#C62828
 */
export function getCalendarEventColors(eventType?: string | null): { bg: string; border: string; text: string } {
  // WHAT: Returns colors from selected ProjectAlpha palette colors (no gold)
  // WHY: Maintain brand consistency using only approved palette colors
  switch ((eventType ?? '').toLowerCase()) {
    case 'actual_liquidation':
      return { bg: '#00796B', border: '#00796B', text: '#ffffff' }; // Info Teal
    case 'projected_liquidation':
      return { bg: '#6B5A7A', border: '#6B5A7A', text: '#ffffff' }; // Muted Plum
    case 'bid_date':
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
 * Helper that maps lifecycle statuses (Active, Liquidated, etc.) to badge tones.
 * EDIT: Extend logic as new lifecycle statuses are introduced.
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
