/**
 * BADGE COLORS - SINGLE SOURCE OF TRUTH
 * ============================================================================
 *
 * WHAT: All badge color tones, mappings, and category color configurations
 * WHY: Centralized badge color definitions separate from global color palette
 * HOW: Import colors from global palette, define badge-specific color mappings
 *
 * ⚠️ IMPORTANT COLOR RULES:
 * ========================
 * 1. ALL COLORS MUST COME FROM GlobalStandardizations/colors/colorPalette.ts
 * 2. DO NOT use hardcoded hex values (e.g., '#FF0000')
 * 3. Use STATUS_COLORS or TAG_COLORS constants
 * 4. Use helper functions: getStatusColor(), getTagColor(), createPaletteBadge()
 *
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
} from '../colors/colorPalette';
import type { BadgeVisualConfig } from './badgeConfig';

// ============================================================================
// 🎨 BADGE TONE TYPE DEFINITIONS
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
  | 'property-multifamily'
  | 'property-land'
  | 'property-mixed-use'
  | 'property-other'
  // Lifecycle status colors
  | 'lifecycle-active'
  | 'lifecycle-liquidated'
  | 'lifecycle-hold'
  | 'lifecycle-default'
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
  | 'tag-steel-gray';

// ============================================================================
// 🌈 BADGE TONE COLOR MAPPINGS
// ============================================================================

/**
 * Badge tone color configurations
 * Maps badge tone keys to visual configurations (classes and inline styles)
 */
export const BADGE_TONE_CONFIG: Record<BadgeToneKey, BadgeVisualConfig> = {
  // ============================================================================
  // Standard Bootstrap Colors
  // ============================================================================
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

  // ============================================================================
  // Track-Specific Colors
  // ============================================================================
  'modification-green': {
    classes: 'bg-success text-white border-0',
    ariaLabel: undefined,
  },

  // ============================================================================
  // Calendar Event Type Colors
  // ============================================================================
  'calendar-liquidation': {
    classes: 'text-white border-0',
    ariaLabel: 'Actual liquidation event',
    inlineStyles: `background-color: ${COLOR_INFO_TEAL};`,
  },
  'calendar-projected': {
    classes: 'text-white border-0',
    ariaLabel: 'Projected liquidation event',
    inlineStyles: `background-color: ${COLOR_MUTED_PLUM};`,
  },
  'calendar-bid': {
    classes: 'text-white border-0',
    ariaLabel: 'Bid date event',
    inlineStyles: `background-color: ${COLOR_STEEL_TEAL};`,
  },
  'calendar-settlement': {
    classes: 'text-white border-0',
    ariaLabel: 'Settlement date event',
    inlineStyles: `background-color: ${COLOR_SLATE_TEAL};`,
  },
  'calendar-follow-up': {
    classes: 'text-white border-0',
    ariaLabel: 'Follow-up reminder event',
    inlineStyles: `background-color: ${COLOR_INDIGO};`,
  },
  'calendar-milestone': {
    classes: 'text-white border-0',
    ariaLabel: 'Milestone event',
    inlineStyles: `background-color: ${COLOR_DUSTY_LAVENDER};`,
  },

  // ============================================================================
  // Delinquency Status Colors
  // ============================================================================
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

  // ============================================================================
  // Property Type Colors (using tag colors from palette)
  // ============================================================================
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

  // ============================================================================
  // Lifecycle Status Colors
  // ============================================================================
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
  // Tag/Category Colors - Main Tags
  // ============================================================================
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

  // ============================================================================
  // Tag/Category Colors - Sub-Tags
  // ============================================================================
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

  // ============================================================================
  // Tag/Category Colors - Blue Variants (Property Types & Classifications)
  // ============================================================================
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
// 🔧 HELPER FUNCTION - Create palette badge
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

// ============================================================================
// 📊 CATEGORY COLOR CONFIGURATIONS (from categoryColors.ts)
// ============================================================================

/**
 * Property Type Category Colors
 * Used in: Property Type column in Asset Grid, Acquisition Grid, etc.
 */
export const PROPERTY_TYPE_COLORS: Record<string, keyof typeof TAG_COLORS> = {
  'SFR': 'eucalyptus',                  // #78A083 - Single Family Residence
  'Single Family': 'moss',               // #6B7C59 - Single Family (alternate)
  'Manufactured': 'stone',              // #9C8B7A - Manufactured Home
  'Condo': 'seafoam',                   // #7A9B8E - Condominium
  'Townhouse': 'mauve',                 // #8B7E8F - Townhouse
  '2-4 Family': 'heather',              // #9B8FA5 - 2-4 Family Property
  'Multifamily 5+': 'graphite',         // #555D62 - Multifamily 5+ Units
  'Multi-Family': 'pewter',             // #8B9196 - Multi-Family Property
  'Land': 'ash',                        // #A8B2B8 - Vacant Land
};

/**
 * Asset Master Status Category Colors
 * Used in: Asset Master Status column in Asset Grid
 */
export const ASSET_MASTER_STATUS_COLORS: Record<string, keyof typeof TAG_COLORS> = {
  'ACTIVE': 'military-green',             // #556B2F - Active Asset Status
  'LIQUIDATED': 'warm-yellow',            // #D4A574 - Liquidated Asset Status
};

/**
 * Loan Performance Status Category Colors
 * Used in: Loan Performance column in various grids
 */
export const LOAN_PERFORMANCE_COLORS: Record<string, keyof typeof TAG_COLORS> = {
  'NPL': 'clay',                          // Non-Performing Loan
  'REO': 'stone',                         // Real Estate Owned
  'PERF': 'eucalyptus',                  // Performing
  'PERFORMING': 'eucalyptus',            // Performing (alternate)
  'RPL': 'navy-blue',                    // Re-Performing Loan
};

/**
 * Asset Pipeline Track Category Colors
 * Used in: Active Tracks column, Active Tasks column
 */
export const ASSET_PIPELINE_TRACK_COLORS: Record<string, keyof typeof TAG_COLORS> = {
  'DIL': 'slate-purple',                 // #6A6478 - Deed in Lieu
  'Modification': 'thyme',               // #5C6B5A - Loan Modification
  'REO': 'mineral-blue',                 // #5D6B79 - Real Estate Owned
  'FC': 'navy-blue',                     // #1B3B5F - Foreclosure Sale
  'Short Sale': 'clay',                  // #A0725F - Short Sale
  'Note Sale': 'heather',                // #9B8FA5 - Note Sale
  'Performing': 'steel-gray',            // #7A8189 - Performing Track
  'Delinquent': 'pewter',                // #8B9196 - Delinquent Track
};
