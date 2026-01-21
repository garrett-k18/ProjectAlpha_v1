/**
 * ProjectAlpha Color Palette - TypeScript Constants
 * ==================================================
 * 
 * SINGLE SOURCE OF TRUTH for colors in TypeScript/JavaScript
 * This file mirrors frontend_vue/src/assets/scss/config/_color-palette.scss
 * 
 * IMPORTANT: When adding/editing colors:
 * 1. Update SCSS file: _color-palette.scss
 * 2. Update this TypeScript file to match
 * 3. Keep hex values in sync between both files
 * 
 * Usage: Import colors from here instead of hardcoding hex values
 */

// ============================================
// PRIMARY PALETTE
// ============================================
export const COLOR_PRIMARY_NAVY = '#1B3B5F';
export const COLOR_ACCENT_GOLD = '#D4AF37';

// ============================================
// NEUTRAL TONES
// ============================================
export const COLOR_CHARCOAL = '#2C3E50';
export const COLOR_SLATE_GRAY = '#6C757D';
export const COLOR_LIGHT_GRAY = '#E9ECEF';
export const COLOR_OFF_WHITE_BEIGE = '#EDE7E1';
export const COLOR_PURE_WHITE = '#FFFFFF';

// ============================================
// SUPPORTING BLUES
// ============================================
export const COLOR_STEEL_BLUE = '#4A6FA5';
export const COLOR_MIDNIGHT_BLUE = '#0F2744';
export const COLOR_SOFT_BLUE = '#8BA8C9';

// ============================================
// WARM ACCENTS
// ============================================
export const COLOR_WARM_TAUPE = '#B8A88E';
export const COLOR_BRONZE = '#CD7F32';
export const COLOR_CREAM = '#F5F3EE';

// ============================================
// STATUS - SUCCESS/POSITIVE
// ============================================
export const COLOR_SUCCESS_GREEN = '#2E7D32';
export const COLOR_EMERALD = '#16A085';
export const COLOR_SAGE_GREEN = '#6B8E6B';

// ============================================
// STATUS - WARNING/CAUTION
// ============================================
export const COLOR_WARNING_AMBER = '#C97A3A';
export const COLOR_HONEY = '#C99A4F';

// ============================================
// STATUS - ERROR/URGENT
// ============================================
export const COLOR_ERROR_RED = '#C62828';
export const COLOR_BURGUNDY = '#8B1538';
export const COLOR_DUSTY_RED = '#B85A4F';

// ============================================
// STATUS - INFORMATIONAL
// ============================================
export const COLOR_INFO_TEAL = '#00796B';
export const COLOR_STEEL_TEAL = '#4A7A8A';
export const COLOR_SLATE_TEAL = '#5A8A95';

// ============================================
// STATUS - NEUTRAL/INACTIVE
// ============================================
export const COLOR_MEDIUM_GRAY = '#95A5A6';
export const COLOR_COOL_GRAY = '#78909C';
export const COLOR_SILVER = '#B0BEC5';

// ============================================
// STATUS - SPECIAL PROCESS
// ============================================
export const COLOR_MUTED_PLUM = '#6B5A7A';
export const COLOR_INDIGO = '#3F51B5';
export const COLOR_DUSTY_LAVENDER = '#8A7A9A';

// ============================================
// STATUS - FINANCIAL
// ============================================
export const COLOR_FOREST_GREEN = '#1B5E20';
export const COLOR_OLIVE = '#827717';
export const COLOR_BURNT_SIENNA = '#B85A3A';

// ============================================
// TAG & CATEGORY COLORS - Main Tags
// ============================================
export const COLOR_CLAY = '#A0725F';
export const COLOR_THYME = '#5C6B5A';
export const COLOR_STONE = '#9C8B7A';
export const COLOR_EUCALYPTUS = '#78A083';
export const COLOR_SEAFOAM = '#7A9B8E';
export const COLOR_MOSS = '#6B7C59';
export const COLOR_MINERAL_BLUE = '#5D6B79';
export const COLOR_UMBER = '#7A5C4D';

// ============================================
// TAG & CATEGORY COLORS - Sub-Tags
// ============================================
export const COLOR_MAUVE = '#8B7E8F';
export const COLOR_HEATHER = '#9B8FA5';
export const COLOR_SLATE_PURPLE = '#6A6478';
export const COLOR_PEWTER = '#8B9196';
export const COLOR_GRAPHITE = '#555D62';
export const COLOR_ASH = '#A8B2B8';

// ============================================
// TAG & CATEGORY COLORS - Blue Variants (For Property Types & Classifications)
// ============================================
export const COLOR_NAVY_BLUE = '#1B3B5F';      // Primary Navy - for primary property types (SFR)
export const COLOR_INFO_BLUE = '#5A8A95';      // Slate Teal - for informational property types (Condo)
export const COLOR_STEEL_GRAY = '#7A8189';    // Muted blue-gray - for secondary property types (Townhouse)

// ============================================
// TAG & CATEGORY COLORS - Status-Specific Tags
// ============================================
export const COLOR_MILITARY_GREEN = '#556B2F'; // Military/olive green for active status
export const COLOR_WARM_YELLOW = '#D4A574';   // Warm golden yellow for liquidated status

// ============================================
// COLOR MAPS - For easy lookup
// ============================================

/**
 * All status colors map - Use for status badges
 */
export const STATUS_COLORS = {
  // Success/Positive
  success: COLOR_SUCCESS_GREEN,
  'success-green': COLOR_SUCCESS_GREEN,
  emerald: COLOR_EMERALD,
  'sage-green': COLOR_SAGE_GREEN,
  'forest-green': COLOR_FOREST_GREEN,
  
  // Warning/Caution
  warning: COLOR_WARNING_AMBER,
  'warning-amber': COLOR_WARNING_AMBER,
  honey: COLOR_HONEY,
  gold: COLOR_ACCENT_GOLD,
  
  // Error/Urgent
  error: COLOR_ERROR_RED,
  'error-red': COLOR_ERROR_RED,
  burgundy: COLOR_BURGUNDY,
  'dusty-red': COLOR_DUSTY_RED,
  
  // Informational
  info: COLOR_INFO_TEAL,
  'info-teal': COLOR_INFO_TEAL,
  'steel-teal': COLOR_STEEL_TEAL,
  'slate-teal': COLOR_SLATE_TEAL,
  
  // Neutral/Inactive
  inactive: COLOR_MEDIUM_GRAY,
  'medium-gray': COLOR_MEDIUM_GRAY,
  'cool-gray': COLOR_COOL_GRAY,
  archived: COLOR_COOL_GRAY,
  silver: COLOR_SILVER,
  disabled: COLOR_SILVER,
  
  // Special Process
  'under-review': COLOR_MUTED_PLUM,
  'muted-plum': COLOR_MUTED_PLUM,
  compliance: COLOR_INDIGO,
  indigo: COLOR_INDIGO,
  'pending-decision': COLOR_DUSTY_LAVENDER,
  'dusty-lavender': COLOR_DUSTY_LAVENDER,
  
  // Financial
  profitable: COLOR_FOREST_GREEN,
  'break-even': COLOR_OLIVE,
  olive: COLOR_OLIVE,
  loss: COLOR_BURNT_SIENNA,
  'burnt-sienna': COLOR_BURNT_SIENNA,
} as const;

/**
 * All tag colors map - Use for tag/category badges
 */
export const TAG_COLORS = {
  // Main Tags
  clay: COLOR_CLAY,
  thyme: COLOR_THYME,
  stone: COLOR_STONE,
  eucalyptus: COLOR_EUCALYPTUS,
  seafoam: COLOR_SEAFOAM,
  moss: COLOR_MOSS,
  'mineral-blue': COLOR_MINERAL_BLUE,
  umber: COLOR_UMBER,
  
  // Sub-Tags
  mauve: COLOR_MAUVE,
  heather: COLOR_HEATHER,
  'slate-purple': COLOR_SLATE_PURPLE,
  pewter: COLOR_PEWTER,
  graphite: COLOR_GRAPHITE,
  ash: COLOR_ASH,
  
  // Blue Variants (Property Types & Classifications)
  'navy-blue': COLOR_NAVY_BLUE,      // Primary Navy - for primary property types (SFR)
  'info-blue': COLOR_INFO_BLUE,      // Slate Teal - for informational property types (Condo)
  'steel-gray': COLOR_STEEL_GRAY,    // Muted blue-gray - for secondary property types (Townhouse)
  
  // Status-Specific Tags
  'military-green': COLOR_MILITARY_GREEN,  // Military/olive green for active status
  'warm-yellow': COLOR_WARM_YELLOW,        // Warm golden yellow for liquidated status
} as const;

/**
 * Helper function to get status color
 * @param statusName - Status color name from STATUS_COLORS map
 * @returns Hex color string
 */
export function getStatusColor(statusName: keyof typeof STATUS_COLORS): string {
  return STATUS_COLORS[statusName] || COLOR_SLATE_GRAY;
}

/**
 * Helper function to get tag color
 * @param tagName - Tag color name from TAG_COLORS map
 * @returns Hex color string
 */
export function getTagColor(tagName: keyof typeof TAG_COLORS): string {
  return TAG_COLORS[tagName] || COLOR_SLATE_GRAY;
}

/**
 * Type-safe color value - Only allows palette colors
 */
export type PaletteColor = 
  | typeof COLOR_PRIMARY_NAVY
  | typeof COLOR_ACCENT_GOLD
  | typeof COLOR_CHARCOAL
  | typeof COLOR_SLATE_GRAY
  | typeof COLOR_LIGHT_GRAY
  | typeof COLOR_OFF_WHITE_BEIGE
  | typeof COLOR_PURE_WHITE
  | typeof COLOR_STEEL_BLUE
  | typeof COLOR_MIDNIGHT_BLUE
  | typeof COLOR_SOFT_BLUE
  | typeof COLOR_WARM_TAUPE
  | typeof COLOR_BRONZE
  | typeof COLOR_CREAM
  | typeof COLOR_SUCCESS_GREEN
  | typeof COLOR_EMERALD
  | typeof COLOR_SAGE_GREEN
  | typeof COLOR_WARNING_AMBER
  | typeof COLOR_HONEY
  | typeof COLOR_ERROR_RED
  | typeof COLOR_BURGUNDY
  | typeof COLOR_DUSTY_RED
  | typeof COLOR_INFO_TEAL
  | typeof COLOR_STEEL_TEAL
  | typeof COLOR_SLATE_TEAL
  | typeof COLOR_MEDIUM_GRAY
  | typeof COLOR_COOL_GRAY
  | typeof COLOR_SILVER
  | typeof COLOR_MUTED_PLUM
  | typeof COLOR_INDIGO
  | typeof COLOR_DUSTY_LAVENDER
  | typeof COLOR_FOREST_GREEN
  | typeof COLOR_OLIVE
  | typeof COLOR_BURNT_SIENNA
  | typeof COLOR_CLAY
  | typeof COLOR_THYME
  | typeof COLOR_STONE
  | typeof COLOR_EUCALYPTUS
  | typeof COLOR_SEAFOAM
  | typeof COLOR_MOSS
  | typeof COLOR_MINERAL_BLUE
  | typeof COLOR_UMBER
  | typeof COLOR_MAUVE
  | typeof COLOR_HEATHER
  | typeof COLOR_SLATE_PURPLE
  | typeof COLOR_PEWTER
  | typeof COLOR_GRAPHITE
  | typeof COLOR_ASH
  | typeof COLOR_MILITARY_GREEN
  | typeof COLOR_WARM_YELLOW;
