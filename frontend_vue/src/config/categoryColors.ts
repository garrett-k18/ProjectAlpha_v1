/**
 * CATEGORY COLOR CONFIGURATION - SINGLE SOURCE OF TRUTH
 * ======================================================
 * 
 * WHAT: Centralized configuration for all category field color assignments
 * WHY: Easy to see and modify color assignments for all classifications in one place
 * HOW: Define categories and their tag color assignments here, then import into badgeTokens.ts
 * 
 * ⚠️ IMPORTANT:
 * - ALL colors must come from TAG_COLORS in colorPalette.ts
 * - Use tag color names (e.g., 'navy-blue', 'info-blue', 'clay')
 * - DO NOT use hardcoded hex values or Bootstrap classes
 * 
 * TO ADD/CHANGE COLORS:
 * 1. Update the color assignment in the relevant category below
 * 2. Use getTagColor() helper to ensure color exists in palette
 * 3. Colors will automatically apply to all grids using these categories
 */

import { getTagColor, type TAG_COLORS } from './colorPalette';

// ============================================================================
// PROPERTY TYPE COLORS
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

// ============================================================================
// ASSET MASTER STATUS COLORS
// ============================================================================
/**
 * Asset Master Status Category Colors
 * Used in: Asset Master Status column in Asset Grid
 */
export const ASSET_MASTER_STATUS_COLORS: Record<string, keyof typeof TAG_COLORS> = {
  'ACTIVE': 'military-green',             // #556B2F - Active Asset Status
  'LIQUIDATED': 'warm-yellow',            // #D4A574 - Liquidated Asset Status
};

// ============================================================================
// LOAN PERFORMANCE STATUS COLORS
// ============================================================================
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

// ============================================================================
// ASSET PIPELINE TRACK COLORS
// ============================================================================
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

// ============================================================================
// HELPER FUNCTIONS - Generate enum maps from color configs
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
// TITLE HELPERS - Human-readable titles for each category value
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
