<template>
  <!--
    Badge renderer for AG Grid cells.
    - Uses Bootstrap/Hyper UI badge classes (no custom CSS) for consistency.
    - Accepts AG Grid params via `params` prop (Vue 3 cell renderer contract).
    - Displays square/slightly rounded badges with contextual color based on boolean/enum value.
    - Supports multi-badge mode for comma-separated values (e.g., "DIL, Modification")
    - Empty/unknown values render as an empty string to keep grid clean.
    - UPDATED: Changed from rounded-pill to rounded for more professional/serious tone
  -->
  <!-- Multi-badge mode: render multiple small badges with gap -->
  <span v-if="badges.length > 1" class="d-inline-flex gap-1 flex-wrap justify-content-center">
    <span 
      v-for="(b, idx) in badges" 
      :key="idx" 
      class="badge rounded fw-semibold" 
      :class="[b.color, sizeClass]"
      :style="sizeStyle"
      :title="b.title"
    >
      {{ b.label }}
    </span>
  </span>
  <!-- Single badge mode -->
  <span v-else-if="badges.length === 1" class="badge rounded fw-semibold" :class="[badges[0].color, sizeClass]" :style="sizeStyle" :title="badges[0].title">
    {{ badges[0].label }}
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
 * Badge size styles based on size parameter ('xs' | 'sm' | 'md' | 'lg')
 * WHAT: Maps size keys to inline CSS for consistent badge dimensions (square style with slight rounding)
 * WHY: Allows small badges for multi-badge cells vs. larger single badges
 * HOW: Returns CSS string for padding, font-size, border-radius based on badgeTokens.ts presets
 */
const sizeStyle = computed(() => {
  const p = props.params || {}
  const size = p?.colDef?.cellRendererParams?.size || p?.cellRendererParams?.size || 'md'
  
  // Size presets matching badgeTokens.ts PILL_DIMENSIONS (square badges with slight rounding)
  const sizeMap: Record<string, string> = {
    xs: 'padding: 0.125rem 0.5rem; font-size: 0.5rem; border-radius: 0.25rem;',
    sm: 'padding: 0.1rem 0.4rem; font-size: 0.7rem; border-radius: 0.25rem;',  // Small preset - reduced padding for compact multi-badge cells
    md: 'padding: 0.25rem 0.75rem; font-size: 0.75rem; border-radius: 0.25rem;',
    lg: 'padding: 0.375rem 1rem; font-size: 0.875rem; border-radius: 0.375rem;',
  }
  
  return sizeMap[size] || sizeMap.md
})

/**
 * Legacy size class for backward compatibility (can be removed if not needed)
 */
const sizeClass = computed(() => {
  const p = props.params || {}
  const size = p?.colDef?.cellRendererParams?.size || p?.cellRendererParams?.size
  // Return empty string - we use inline styles now
  return ''
})

/**
 * Badge configs computed from value and optional renderer params.
 * params.cellRendererParams can specify:
 * - mode: 'boolean' | 'enum' | 'multi' | 'multi-prefix'
 * - enumMap: Record<string, { label: string; color: string; title?: string }> (for 'enum' and 'multi' modes)
 * - colorMap: Record<string, string> (for 'multi-prefix' mode - maps prefix to color class)
 * - size: 'xs' | 'sm' | 'md' | 'lg'
 */
const badges = computed(() => {
  const p = props.params || {}
  const value = p.value
  const mode = p?.colDef?.cellRendererParams?.mode || p?.cellRendererParams?.mode
  const enumMap = p?.colDef?.cellRendererParams?.enumMap || p?.cellRendererParams?.enumMap || {}

  // Multi mode: split comma-separated values and render multiple badges
  // WHAT: Supports fields like "DIL, Modification" with individual colored pills
  // WHY: Active Tracks field contains multiple workflow types per asset
  // HOW: Split by comma, trim, look up each value in enumMap, return array of badge configs
  if (mode === 'multi') {
    if (value === null || value === undefined || value === '') return []
    const values = String(value).split(',').map(v => v.trim()).filter(v => v.length > 0)
    const result = []
    for (const val of values) {
      const found = enumMap[val] || enumMap[val.toLowerCase?.()] || enumMap[String(val).toLowerCase?.()]
      if (found) {
        result.push({
          label: found.label ?? val,
          color: found.color ?? 'bg-secondary',
          title: found.title ?? val
        })
      }
    }
    return result
  }

  // Multi-prefix mode: split comma-separated values, color by prefix before colon
  // WHAT: Supports fields like "DIL: Owner/Heirs contacted, Modification: Drafted"
  // WHY: Active Tasks field contains outcome prefix + task description
  // HOW: Split by comma, extract prefix before ":", look up color from colorMap, display only task description after colon
  if (mode === 'multi-prefix') {
    if (value === null || value === undefined || value === '') return []
    const colorMap = p?.colDef?.cellRendererParams?.colorMap || p?.cellRendererParams?.colorMap || {}
    const values = String(value).split(',').map(v => v.trim()).filter(v => v.length > 0)
    const result = []
    for (const val of values) {
      // Extract prefix before colon (e.g., "DIL" from "DIL: Owner contacted")
      const colonIndex = val.indexOf(':')
      const prefix = colonIndex > 0 ? val.substring(0, colonIndex).trim() : val
      const taskDescription = colonIndex > 0 ? val.substring(colonIndex + 1).trim() : val
      const color = colorMap[prefix] || 'bg-secondary'
      result.push({
        label: taskDescription,  // Only the task description after the colon (e.g., "Pursuing DIL" instead of "DIL: Pursuing DIL")
        color: color,
        title: val  // Keep full text in tooltip for context
      })
    }
    return result
  }

  // Boolean mode: render Yes/No pills based on common truthy/falsy values
  if (mode === 'boolean') {
    const b = toBoolLike(value)
    if (b === null) return []
    // Allow overrides via cellRendererParams for color theming
    const yesColor = p?.colDef?.cellRendererParams?.booleanYesColor || p?.cellRendererParams?.booleanYesColor || 'bg-danger'
    const noColor = p?.colDef?.cellRendererParams?.booleanNoColor || p?.cellRendererParams?.booleanNoColor || 'bg-warning text-white'
    return [b
      ? { label: 'Yes', color: yesColor, title: 'True' }
      : { label: 'No', color: noColor, title: 'False' }]
  }

  // Enum mode: look up by string key (case-insensitive)
  // WHAT: Strict enum matching - no fallbacks, no guessing
  // WHY: If data not in backend, don't display anything (user requirement)
  // HOW: Return empty array if value not found in enumMap
  if (mode === 'enum') {
    if (value === null || value === undefined || value === '') return []
    const key = String(value).trim()
    // Try exact match, then case-insensitive
    const found = enumMap[key] || enumMap[key.toLowerCase?.()] || enumMap[String(value).toLowerCase?.()]
    if (found) {
      // Normalize label/color and force 'Default' to yellow for clarity
      const label = found.label ?? key
      const color = found.color ?? 'bg-warning text-white'
      const adjustedColor = String(label).trim().toLowerCase() === 'default' ? 'bg-warning text-white' : color
      return [{ label, color: adjustedColor, title: found.title ?? key }]
    }
    // NO FALLBACK: If enum value not in map, return empty array (show nothing)
    return []
  }

  // If mode is unspecified, try boolean detection first
  const b = toBoolLike(value)
  if (b !== null) {
    return [b
      ? { label: 'Yes', color: 'bg-primary', title: 'True' }
      : { label: 'No', color: 'bg-warning text-white', title: 'False' }]
  }
  
  // NO FALLBACK: If no mode specified and not boolean, return empty array (show nothing)
  return []
})
</script>
