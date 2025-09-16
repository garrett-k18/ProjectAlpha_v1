<template>
  <!--
    AssetHeader
    - Reusable header component that supports both modal and full-page (card) contexts.
    - Props allow toggling a primary action button (e.g., "Open full page") and a close button.
    - Emits events instead of performing navigation/closing directly, so parents control behavior.
    - When used inside BootstrapVue's <b-modal> header slot, set wrap=false to avoid nested wrappers.
  -->
  <!-- Wrapped variant (modal-header or card-header) -->
  <div v-if="wrapComputed" :class="wrapperClass">
    <div class="d-flex align-items-center w-100">
      <h4 :class="titleClass">{{ title }}</h4>
      <div class="ms-auto d-flex align-items-center gap-2">
        <button
          v-if="showPrimaryAction"
          type="button"
          class="btn btn-sm btn-primary"
          :title="primaryTitle || primaryActionLabel"
          :disabled="primaryDisabled"
          @click="emit('primary')"
        >
          {{ primaryActionLabel }}
        </button>
        <button
          v-if="finalShowClose"
          type="button"
          class="btn-close"
          aria-label="Close"
          @click="emit('close')"
        ></button>
      </div>
    </div>
  </div>

  <!-- Bare variant for slots (no wrapper) -->
  <div v-else class="d-flex align-items-center w-100">
    <h4 :class="titleClass">{{ title }}</h4>
    <div class="ms-auto d-flex align-items-center gap-2">
      <button
        v-if="showPrimaryAction"
        type="button"
        class="btn btn-sm btn-primary"
        :title="primaryTitle || primaryActionLabel"
        :disabled="primaryDisabled"
        @click="emit('primary')"
      >
        {{ primaryActionLabel }}
      </button>
      <button
        v-if="finalShowClose"
        type="button"
        class="btn-close"
        aria-label="Close"
        @click="emit('close')"
      ></button>
    </div>
  </div>
</template>

<script setup lang="ts">
// Props definition with sensible defaults for both modal and page contexts.
// We keep behavior generic so the component can be reused widely.

// Import Vue utilities for typing and computed state.
import { computed } from 'vue'

// Define the public props interface.
interface Props {
  /**
   * title
   * - Text shown in the header. For modal variant, the element uses the
   *   Bootstrap `modal-title` class to match native styling.
   */
  title: string

  /**
   * variant
   * - Controls styling/layout specifics:
   *   'modal' -> wraps with `modal-header` and uses `modal-title`
   *   'page'  -> wraps with `card-header` and uses standard heading class
   */
  variant?: 'modal' | 'page'

  /**
   * showClose
   * - Whether to display a close (X) button. Defaults to true for modal variant,
   *   false for page variant. Parent handles the actual close behavior via @close.
   */
  showClose?: boolean

  /**
   * showPrimaryAction
   * - Whether to display the primary action button (e.g., "Open full page").
   */
  showPrimaryAction?: boolean

  /**
   * primaryActionLabel
   * - Label text for the primary action button.
   */
  primaryActionLabel?: string

  /**
   * primaryTitle
   * - Optional title attribute for the primary action button (tooltip on hover).
   */
  primaryTitle?: string

  /**
   * primaryDisabled
   * - Disabled state for the primary action button.
   */
  primaryDisabled?: boolean

  /**
   * wrap
   * - Whether to render the wrapper element (modal-header/card-header).
   *   Set to false when placing inside a <b-modal> header slot which already
   *   provides the header container.
   */
  wrap?: boolean
}

// Provide default values using withDefaults for optional props.
const props = withDefaults(defineProps<Props>(), {
  variant: 'modal',
  showClose: undefined, // If undefined, we infer based on variant below
  showPrimaryAction: false,
  primaryActionLabel: 'Action',
  primaryTitle: '',
  primaryDisabled: false,
  wrap: true,
})

// Declare emitted events so parent components can act on them.
const emit = defineEmits<{
  /** Emitted when the primary action button is clicked */
  (e: 'primary'): void
  /** Emitted when the close (X) button is clicked */
  (e: 'close'): void
}>()

/**
 * finalShowClose
 * - If showClose was not explicitly provided, default to true for modal variant
 *   and false for page variant.
 */
const finalShowClose = computed<boolean>(() => {
  if (props.showClose === undefined) return props.variant === 'modal'
  return props.showClose
})

/**
 * wrapperClass
 * - Chooses appropriate wrapper class depending on the variant.
 */
const wrapperClass = computed<string>(() =>
  props.variant === 'modal' ? 'modal-header' : 'card-header'
)

/**
 * titleClass
 * - Chooses the correct title class for the variant.
 */
const titleClass = computed<string>(() =>
  props.variant === 'modal' ? 'modal-title mb-0' : 'h4 header-title mb-0'
)

// Expose only what templates need (script setup auto-exposes props/computed)
const showPrimaryAction = computed(() => props.showPrimaryAction)
const primaryActionLabel = computed(() => props.primaryActionLabel)
const primaryTitle = computed(() => props.primaryTitle)
const primaryDisabled = computed(() => props.primaryDisabled)
const wrapComputed = computed<boolean>(() => props.wrap)
</script>

<style scoped>
/* No specific styles added here; we rely on Bootstrap/Hyper UI utility classes.
   Scoped style block included for future adjustments if needed. */
</style>
