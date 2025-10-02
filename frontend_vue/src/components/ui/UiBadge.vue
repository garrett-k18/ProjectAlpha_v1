<!--
  UiBadge.vue
  ---------------------------------------------------------------------------
  A tiny presentation wrapper for badge/pill UI that defers styling decisions
  to `@/config/badgeTokens.ts`. This separation allows for maximum reusability across
  Vue components, Pinia stores, and even plain TypeScript utilities, while
  keeping the component itself very lightweight. Hyper UI badge reference:
  https://hyperui.dev/components/badges
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
    :aria-label="computedAriaLabel"
    role="status"
    style="line-height: 1; padding-top: 0.6rem; padding-bottom: 0.5rem;"
  >
    <!-- Allow callers to override the content via default slot; fall back to provided label -->
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { withDefaults, defineProps } from 'vue'
import type { BadgeToneKey, BadgeSizeKey } from '@/config/badgeTokens'
import { resolveBadgeTokens } from '@/config/badgeTokens'

/**
 * Props for `UiBadge`.
 * - `tone` selects the color palette.
 * - `size` selects the spacing + font scale (defaults to `md`).
 * - `label` provides inline text when the slot is unused.
 * - `ariaLabel` lets callers override the accessible description when needed.
 */
const props = withDefaults(defineProps<{
  tone: BadgeToneKey
  size?: BadgeSizeKey
  label?: string | number | null
  ariaLabel?: string | null
}>(), {
  size: 'md',
  label: null,
  ariaLabel: null,
})

/**
 * Resolve merged classes + aria label from centralized badge token map.
 */
const tokens = computed(() => resolveBadgeTokens(props.tone, props.size))

/**
 * Extract the final class list. We memoize via computed to avoid recalculation.
 */
const resolvedClasses = computed(() => tokens.value.classes)

/**
 * Compute the aria-label hierarchy (explicit prop overrides token defaults).
 */
const computedAriaLabel = computed(() => props.ariaLabel ?? tokens.value.ariaLabel ?? undefined)

/**
 * Normalize label to a string for template fallback rendering.
 */
const label = computed(() => (props.label ?? '').toString())
</script>
