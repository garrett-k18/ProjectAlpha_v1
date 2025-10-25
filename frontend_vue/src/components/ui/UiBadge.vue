<!--
  UiBadge.vue - SINGLE SOURCE OF TRUTH PRESENTATION LAYER
  ---------------------------------------------------------------------------
  Pure presentation component that renders badges using centralized styling from
  `@/config/badgeTokens.ts`. ALL styling logic consolidated in badgeTokens.ts.
  WHAT: Lightweight Vue wrapper for badge rendering
  WHY: Eliminates dual styling sources and CSS conflicts
  HOW: Consumes complete styling from badgeTokens.ts (classes + inline styles)
  Hyper UI badge reference: https://hyperui.dev/components/badges
-->
<template>
  <!--
    UI Badge component following Hyper UI guidance.
    Documentation reviewed: https://hyperui.dev/components/badges
    Renders a stylized pill that accepts a tone + size and optional label override.
  -->
  <span
    v-if="resolvedClasses"
    :class="resolvedClasses"
    :style="resolvedInlineStyles"
    :aria-label="computedAriaLabel"
    :title="hoverTitle"
    role="status"
  >
    <!-- Allow callers to override the content via default slot; fall back to provided label -->
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BadgeToneKey, BadgeSizeKey } from '@/config/badgeTokens'
import { resolveBadgeTokens } from '@/config/badgeTokens'

// ============================================================================
// PROPS - Simple badge component interface
// ============================================================================

const props = withDefaults(defineProps<{
  tone: BadgeToneKey           // Color theme (primary, secondary, etc.)
  size?: BadgeSizeKey          // Size variant (xs, sm, md, lg)
  label?: string | number | null // Text content when not using slot
  ariaLabel?: string | null    // Custom accessibility label
}>(), {
  size: 'md',
  label: null,
  ariaLabel: null,
})

// ============================================================================
// COMPUTED PROPERTIES - All styling resolved from badgeTokens.ts
// ============================================================================

/** Get complete styling configuration from badgeTokens.ts */
const tokens = computed(() => resolveBadgeTokens(props.tone, props.size))

/** CSS classes for the badge */
const resolvedClasses = computed(() => tokens.value.classes)

/** Inline styles for precise control */
const resolvedInlineStyles = computed(() => tokens.value.inlineStyles)

/** Accessibility label with fallback hierarchy */
const computedAriaLabel = computed(() => props.ariaLabel ?? tokens.value.ariaLabel ?? undefined)

/** Display label as string */
const label = computed(() => (props.label ?? '').toString())

/** Hover tooltip with priority: custom > token > label */
const hoverTitle = computed(() => {
  if (props.ariaLabel) return props.ariaLabel
  if (tokens.value.ariaLabel) return tokens.value.ariaLabel
  const l = props.label
  return l != null ? String(l) : undefined
})
</script>
