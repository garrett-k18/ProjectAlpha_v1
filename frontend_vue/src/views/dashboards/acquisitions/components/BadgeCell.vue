<template>
  <!--
    Pill badge renderer for AG Grid cells.
    - Uses Bootstrap/Hyper UI badge classes (no custom CSS) for consistency.
    - Accepts AG Grid params via `params` prop (Vue 3 cell renderer contract).
    - Displays a rounded-pill badge with contextual color based on boolean/enum value.
    - Empty/unknown values render as an empty string to keep grid clean.
  -->
  <!--
    Increase visual size using Bootstrap utilities:
    - px-3 / py-1: larger pill body
    - fs-6: larger font size (utility uses !important to override .badge)
    - fw-semibold: slightly heavier weight for readability
  -->
  <span v-if="badge" class="badge rounded-pill px-3 py-1 fs-6 fw-semibold" :class="badge.color" :title="badge.title">
    {{ badge.label }}
  </span>
  <span v-else></span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * AG Grid passes a single `params` object to Vue cell renderers.
 * We keep it typed as `any` for compatibility across grid versions.
 */
const props = defineProps<{ params: any }>()

/**
 * Normalize truthy/falsy inputs commonly seen in data tapes.
 * Supports: true/false, 1/0, 'Y'/'N', 'Yes'/'No', 'True'/'False'.
 */
function toBoolLike(v: unknown): boolean | null {
  if (v === null || v === undefined || v === '') return null
  const t = typeof v
  if (t === 'boolean') return v as boolean
  if (t === 'number') return Number(v) === 1 ? true : Number(v) === 0 ? false : null
  const s = String(v).trim().toLowerCase()
  if (['y', 'yes', 'true', 't', '1'].includes(s)) return true
  if (['n', 'no', 'false', 'f', '0'].includes(s)) return false
  return null
}

/**
 * Badge config computed from value and optional renderer params.
 * params.cellRendererParams can specify:
 * - mode: 'boolean' | 'enum'
 * - enumMap: Record<string, { label: string; color: string; title?: string }>
 */
const badge = computed(() => {
  const p = props.params || {}
  const value = p.value
  const mode = p?.colDef?.cellRendererParams?.mode || p?.cellRendererParams?.mode
  const enumMap = p?.colDef?.cellRendererParams?.enumMap || p?.cellRendererParams?.enumMap || {}

  // Boolean mode: render Yes/No pills based on common truthy/falsy values
  if (mode === 'boolean') {
    const b = toBoolLike(value)
    if (b === null) return null
    // Allow overrides via cellRendererParams for color theming
    const yesColor = p?.colDef?.cellRendererParams?.booleanYesColor || p?.cellRendererParams?.booleanYesColor || 'bg-danger'
    const noColor = p?.colDef?.cellRendererParams?.booleanNoColor || p?.cellRendererParams?.booleanNoColor || 'bg-warning text-dark'
    return b
      ? { label: 'Yes', color: yesColor, title: 'True' }
      : { label: 'No', color: noColor, title: 'False' }
  }

  // Enum mode: look up by string key (case-insensitive)
  // WHAT: Strict enum matching - no fallbacks, no guessing
  // WHY: If data not in backend, don't display anything (user requirement)
  // HOW: Return null if value not found in enumMap
  if (mode === 'enum') {
    if (value === null || value === undefined || value === '') return null
    const key = String(value).trim()
    // Try exact match, then case-insensitive
    const found = enumMap[key] || enumMap[key.toLowerCase?.()] || enumMap[String(value).toLowerCase?.()]
    if (found) {
      // Normalize label/color and force 'Default' to yellow for clarity
      const label = found.label ?? key
      const color = found.color ?? 'bg-warning text-dark'
      const adjustedColor = String(label).trim().toLowerCase() === 'default' ? 'bg-warning text-dark' : color
      return { label, color: adjustedColor, title: found.title ?? key }
    }
    // NO FALLBACK: If enum value not in map, return null (show nothing)
    return null
  }

  // If mode is unspecified, try boolean detection first
  const b = toBoolLike(value)
  if (b !== null) {
    return b
      ? { label: 'Yes', color: 'bg-primary', title: 'True' }
      : { label: 'No', color: 'bg-warning text-dark', title: 'False' }
  }
  
  // NO FALLBACK: If no mode specified and not boolean, return null (show nothing)
  return null
})
</script>
