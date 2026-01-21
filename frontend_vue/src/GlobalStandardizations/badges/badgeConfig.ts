/**
 * BADGE CONFIGURATION - SINGLE SOURCE OF TRUTH
 * ============================================================================
 *
 * WHAT: Master badge configuration for sizes, dimensions, and base styling
 * WHY: Centralized control of all badge visual properties
 * HOW: Define master variables here, used by all badge components
 *
 * Documentation: https://hyperui.dev/components/badges
 * ============================================================================
 */

// ============================================================================
// 🎨 MASTER SIZING VARIABLES - EDIT THESE TO CHANGE ALL BADGE DIMENSIONS
// ============================================================================

/**
 * Master badge dimensions - Change these values to adjust all badge sizes globally
 * Style: Square badges with slight border-radius for professional appearance
 */
export const BADGE_DIMENSIONS = {
  xs: {
    paddingX: '0.5rem',       // Horizontal padding
    paddingY: '0.125rem',     // Tight vertical padding
    fontSize: '0.5rem',       // Very small text
    borderRadius: '0.25rem'   // Slightly rounded square
  },
  xs2: {
    paddingX: '0.5rem',       // Horizontal padding
    paddingY: '0.16rem',      // Between xs and sm for denser grids
    fontSize: '0.6rem',       // Between xs and sm for readability
    borderRadius: '0.25rem'   // Slightly rounded square
  },
  sm: {
    paddingX: '0.5rem',       // Horizontal padding
    paddingY: '0.2rem',       // Small vertical padding
    fontSize: '0.7rem',       // Small font size
    borderRadius: '0.25rem'   // Slightly rounded square
  },
  md: {
    paddingX: '0.75rem',      // Medium horizontal padding
    paddingY: '0.25rem',      // Medium vertical padding
    fontSize: '0.75rem',      // Medium font size
    borderRadius: '0.25rem'   // Slightly rounded square
  },
  lg: {
    paddingX: '1rem',         // Large horizontal padding
    paddingY: '0.375rem',     // Large vertical padding
    fontSize: '0.875rem',     // Large font size
    borderRadius: '0.375rem'  // Slightly more rounded for larger badges
  }
} as const;

// ============================================================================
// 🏗️ TYPE DEFINITIONS
// ============================================================================

/**
 * Badge size type - keys from BADGE_DIMENSIONS
 */
export type BadgeSizeKey = keyof typeof BADGE_DIMENSIONS;

/**
 * Badge visual configuration object
 */
export interface BadgeVisualConfig {
  /** Tailwind/Bootstrap classes for styling */
  classes: string;
  /** Optional ARIA label for accessibility */
  ariaLabel?: string;
  /** Inline CSS styles for precise control */
  inlineStyles?: string;
}

/**
 * Complete badge token result after merging size + tone
 */
export interface BadgeTokenResult {
  /** Computed class string after merging size + tone */
  classes: string;
  /** Optional ARIA label for accessibility */
  ariaLabel?: string;
  /** Optional inline styles for precise control */
  inlineStyles?: string;
}

// ============================================================================
// 📏 BASE SIZE CONFIGURATIONS
// ============================================================================

/**
 * Base badge size configurations built from BADGE_DIMENSIONS
 * These provide the foundational styling without color
 * EDIT BADGE_DIMENSIONS above to change all badge sizes globally
 */
export const BADGE_SIZE_CONFIG: Record<BadgeSizeKey, BadgeVisualConfig> = {
  xs: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${BADGE_DIMENSIONS.xs.paddingY} ${BADGE_DIMENSIONS.xs.paddingX}; font-size: ${BADGE_DIMENSIONS.xs.fontSize}; border-radius: ${BADGE_DIMENSIONS.xs.borderRadius};`,
  },
  xs2: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${BADGE_DIMENSIONS.xs2.paddingY} ${BADGE_DIMENSIONS.xs2.paddingX}; font-size: ${BADGE_DIMENSIONS.xs2.fontSize}; border-radius: ${BADGE_DIMENSIONS.xs2.borderRadius};`,
  },
  sm: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${BADGE_DIMENSIONS.sm.paddingY} ${BADGE_DIMENSIONS.sm.paddingX}; font-size: ${BADGE_DIMENSIONS.sm.fontSize}; border-radius: ${BADGE_DIMENSIONS.sm.borderRadius};`,
  },
  md: {
    classes: 'badge rounded fw-semibold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${BADGE_DIMENSIONS.md.paddingY} ${BADGE_DIMENSIONS.md.paddingX}; font-size: ${BADGE_DIMENSIONS.md.fontSize}; border-radius: ${BADGE_DIMENSIONS.md.borderRadius};`,
  },
  lg: {
    classes: 'badge rounded fw-bold d-inline-flex align-items-center justify-content-center',
    ariaLabel: undefined,
    inlineStyles: `line-height: 1; padding: ${BADGE_DIMENSIONS.lg.paddingY} ${BADGE_DIMENSIONS.lg.paddingX}; font-size: ${BADGE_DIMENSIONS.lg.fontSize}; border-radius: ${BADGE_DIMENSIONS.lg.borderRadius};`,
  },
};

// ============================================================================
// 🔧 UTILITY FUNCTIONS
// ============================================================================

/**
 * Utility: normalize various boolean-ish values into Yes/No/— labels
 * Supports: true/false, 1/0, 'Y'/'N', 'Yes'/'No', 'True'/'False'
 */
export function toYesNoLabel(v: any): string {
  if (v === true || v === 'true' || v === 'True' || v === 'YES' || v === 'Yes' || v === 'Y' || v === 1) return 'Yes';
  if (v === false || v === 'false' || v === 'False' || v === 'NO' || v === 'No' || v === 'N' || v === 0) return 'No';
  return '—';
}
