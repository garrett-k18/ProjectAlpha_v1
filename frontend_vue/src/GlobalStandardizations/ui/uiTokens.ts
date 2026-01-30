/**
 * UI DESIGN TOKENS - Global Standardization
 * ============================================================================
 *
 * WHAT: Centralized UI design tokens for consistent styling across all components
 * WHY: Eliminate hardcoded values and ensure visual consistency
 * HOW: Import these tokens in components instead of using magic numbers/strings
 *
 * USAGE:
 * import { UI_BACKGROUNDS, UI_SPACING, UI_TYPOGRAPHY, UI_SHADOWS } from '@/GlobalStandardizations/ui'
 *
 * ============================================================================
 */

import { COLOR_CREAM, COLOR_PURE_WHITE, COLOR_LIGHT_GRAY } from '../colors/colorPalette'

// ============================================================================
// 🎨 BACKGROUND COLORS
// ============================================================================

/**
 * WHAT: Standard background colors used across the application
 * WHY: Consistent card/panel backgrounds without hardcoding hex values
 * HOW: Use these constants instead of inline colors
 */
export const UI_BACKGROUNDS = {
  /** Main card background - off-white/cream (#FDFBF7) */
  CARD_PRIMARY: '#FDFBF7',
  
  /** Pure white background for contrast areas */
  CARD_WHITE: COLOR_PURE_WHITE,
  
  /** Light gray background for subtle sections */
  CARD_LIGHT: COLOR_LIGHT_GRAY,
  
  /** Cream background for warm sections */
  CARD_CREAM: COLOR_CREAM,
} as const

// ============================================================================
// 📏 SPACING SCALE
// ============================================================================

/**
 * WHAT: Standardized spacing values (in rem units)
 * WHY: Consistent spacing across all components
 * HOW: Use these instead of arbitrary Bootstrap spacing classes
 */
export const UI_SPACING = {
  /** Extra small spacing - 0.25rem (4px) */
  XS: '0.25rem',
  
  /** Small spacing - 0.5rem (8px) */
  SM: '0.5rem',
  
  /** Medium spacing - 0.75rem (12px) */
  MD: '0.75rem',
  
  /** Base spacing - 1rem (16px) */
  BASE: '1rem',
  
  /** Large spacing - 1.25rem (20px) */
  LG: '1.25rem',
  
  /** Extra large spacing - 1.5rem (24px) */
  XL: '1.5rem',
  
  /** 2X large spacing - 2rem (32px) */
  XXL: '2rem',
} as const

// ============================================================================
// 🔤 TYPOGRAPHY SCALE
// ============================================================================

/**
 * WHAT: Standardized font sizes for consistent typography
 * WHY: Eliminate arbitrary font-size values across components
 * HOW: Use these constants for all text sizing
 */
export const UI_TYPOGRAPHY = {
  /** Extra small text - 0.7rem (11.2px) */
  XS: '0.7rem',
  
  /** Small text - 0.875rem (14px) - Bootstrap small */
  SM: '0.875rem',
  
  /** Base text - 0.95rem (15.2px) */
  BASE: '0.95rem',
  
  /** Medium text - 1rem (16px) */
  MD: '1rem',
  
  /** Large text - 1.125rem (18px) */
  LG: '1.125rem',
  
  /** Extra large text - 1.5rem (24px) */
  XL: '1.5rem',
  
  /** 2X large text - 2rem (32px) - KPI numbers */
  XXL: '2rem',
  
  /** 3X large text - 2.5rem (40px) */
  XXXL: '2.5rem',
} as const

// ============================================================================
// 🎭 SHADOWS
// ============================================================================

/**
 * WHAT: Standardized box shadow values
 * WHY: Consistent elevation/depth across cards and modals
 * HOW: Use these for box-shadow CSS property
 */
export const UI_SHADOWS = {
  /** Subtle shadow for cards - Bootstrap default */
  CARD: '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)',
  
  /** Small shadow for hover states */
  SM: '0 0.125rem 0.5rem rgba(0, 0, 0, 0.1)',
  
  /** Medium shadow for elevated elements */
  MD: '0 0.25rem 0.75rem rgba(0, 0, 0, 0.15)',
  
  /** Large shadow for modals and dropdowns */
  LG: '0 0.5rem 1rem rgba(0, 0, 0, 0.15)',
  
  /** No shadow */
  NONE: 'none',
} as const

// ============================================================================
// 📐 BORDER RADIUS
// ============================================================================

/**
 * WHAT: Standardized border radius values
 * WHY: Consistent rounded corners across all cards/buttons
 * HOW: Use these for border-radius CSS property
 */
export const UI_RADIUS = {
  /** Small radius - 0.25rem (4px) */
  SM: '0.25rem',
  
  /** Base radius - 0.375rem (6px) - Bootstrap default */
  BASE: '0.375rem',
  
  /** Medium radius - 0.5rem (8px) */
  MD: '0.5rem',
  
  /** Large radius - 0.75rem (12px) */
  LG: '0.75rem',
  
  /** Pill radius - 50rem (fully rounded) */
  PILL: '50rem',
  
  /** No radius */
  NONE: '0',
} as const

// ============================================================================
// 📦 CARD PADDING PRESETS
// ============================================================================

/**
 * WHAT: Standardized padding values for card components
 * WHY: Consistent internal spacing across all cards
 * HOW: Use these for card-body, card-header padding
 */
export const UI_CARD_PADDING = {
  /** Tight padding - 0.75rem */
  TIGHT: '0.75rem',
  
  /** Base padding - 1rem (Bootstrap p-3) */
  BASE: '1rem',
  
  /** Comfortable padding - 1.25rem */
  COMFORTABLE: '1.25rem',
  
  /** Spacious padding - 1.5rem */
  SPACIOUS: '1.5rem',
} as const

// ============================================================================
// 🎯 COMPONENT-SPECIFIC TOKENS
// ============================================================================

/**
 * WHAT: Tokens specific to AM Tasking components
 * WHY: Centralize all AM-specific styling decisions
 * HOW: Import and use in AM tasking components
 */
export const AM_TASKING_TOKENS = {
  /** Background color for all AM cards/panels */
  BACKGROUND: UI_BACKGROUNDS.CARD_PRIMARY,
  
  /** Card padding for AM cards */
  CARD_PADDING: UI_CARD_PADDING.COMFORTABLE,
  
  /** Gap between cards in grid layouts */
  CARD_GAP: UI_SPACING.BASE,
  
  /** Border radius for AM cards */
  CARD_RADIUS: UI_RADIUS.BASE,
  
  /** Box shadow for AM cards */
  CARD_SHADOW: UI_SHADOWS.CARD,
  
  /** Header title font size */
  HEADER_TITLE_SIZE: UI_TYPOGRAPHY.LG,
  
  /** KPI number font size */
  KPI_NUMBER_SIZE: UI_TYPOGRAPHY.XXL,
  
  /** KPI title font size */
  KPI_TITLE_SIZE: UI_TYPOGRAPHY.SM,
  
  /** Small text size for labels/metadata */
  SMALL_TEXT_SIZE: UI_TYPOGRAPHY.SM,
  
  /** Task title font size */
  TASK_TITLE_SIZE: UI_TYPOGRAPHY.BASE,
} as const

// ============================================================================
// 📤 EXPORTS
// ============================================================================

export type UIBackground = keyof typeof UI_BACKGROUNDS
export type UISpacing = keyof typeof UI_SPACING
export type UITypography = keyof typeof UI_TYPOGRAPHY
export type UIShadow = keyof typeof UI_SHADOWS
export type UIRadius = keyof typeof UI_RADIUS
export type UICardPadding = keyof typeof UI_CARD_PADDING
