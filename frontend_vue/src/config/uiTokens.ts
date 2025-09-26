/**
 * uiTokens.ts
 * Centralized design tokens and small helpers for the AM Tasking UI.
 *
 * Purpose
 * - Keep spacing, radii, and sizes consistent across outcome cards.
 * - Provide small utility helpers that can be imported into components.
 * - Works alongside theme.css variables for runtime theming.
 *
 * Usage
 * import { uiTokens } from '@/config/uiTokens'
 * const gap = uiTokens.spacing.compactGap; // '0.25rem'
 */

export const uiTokens = {
  spacing: {
    compactGap: '0.25rem', // aligns with Bootstrap g-1
    compactPadding: '0.25rem',
  },
  radius: {
    sm: '0.25rem',
    md: '0.5rem',
  },
  forms: {
    size: 'sm', // default form size across cards
    helperTextVisible: false, // avoid helper text in compact layouts
  },
  header: {
    clickable: true,
  },
} as const

export type UiTokens = typeof uiTokens
