<template>
  <!--
    WHAT
    - This is a small input box for entering money-like numbers.
    - It shows a prefix (like $) and adds commas while you type (1,234.56).

    WHY
    - Users can read large numbers more easily with commas.
    - The app needs a clean number to save (no $ or commas).
      So we format the text you see, but send a plain number to the parent.

    WHERE
    - Place this anywhere you need a compact currency input.
    - Example: DIL card → Cash-for-Keys field.

    HOW (key rules)
    - You pass in v-model (the real value). We turn it into a nice display.
    - As you type, we keep the real value clean (digits and one dot only).
    - We can wait a little before telling the parent (debounce) to reduce saves.

    Quick usage
    <UiCurrencyInput v-model="price" prefix="$" :debounceMs="300" />
  -->
  <div class="input-group" :class="sizeClass">
    <span v-if="prefix" class="input-group-text">{{ prefix }}</span>
    <input
      type="text"
      class="form-control"
      :class="sizeClassControl"
      :placeholder="placeholder"
      :value="display"
      @input="handleInput"
    />
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, defineEmits, ref, watch, computed } from 'vue'

// PROPS (what you can set from the parent component)
// - modelValue: the real value the rest of the app uses (no commas, no $)
// - prefix: what to show at the start of the input (e.g., "$")
// - debounceMs: wait time before telling the parent about changes
// - size: small/medium/large input sizing to match the surrounding UI
// - placeholder: faint example text when empty
const props = withDefaults(defineProps<{
  modelValue: string | number | null
  prefix?: string
  debounceMs?: number
  size?: 'sm' | 'md' | 'lg'
  placeholder?: string
}>(), {
  prefix: '$',
  debounceMs: 0,
  size: 'sm',
  placeholder: '0'
})

// EMITS (what we tell the parent)
// - update:modelValue: we send a clean numeric string like "1234.56"
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

// INTERNAL DISPLAY
// We keep a separate copy of the text as shown to the user (with commas).
const display = ref('')

// TURN INCOMING MODEL VALUE INTO DISPLAY TEXT
// Example: 1234.56 (from parent) → "1,234.56" (what the user sees)
function toDisplay(val: unknown): string {
  if (val == null || val === '') return ''
  const raw = String(val).replace(/[^0-9.]/g, '')
  return formatNumberWithCommas(raw)
}

// TURN DISPLAY TEXT BACK INTO CLEAN MODEL VALUE
// Example: "$1,234.56" → "1234.56" (no $ and no commas)
function toModel(val: string): string {
  if (!val) return ''
  return val.replace(/[^0-9.]/g, '')
}

function formatNumberWithCommas(n: string): string {
  if (!n) return ''
  const [intPart, decPart] = n.split('.')
  const withCommas = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  return decPart !== undefined ? `${withCommas}.${decPart}` : withCommas
}

// KEEP DISPLAY IN SYNC WHEN THE PARENT CHANGES THE VALUE
// (for example after a save comes back from the server)
watch(() => props.modelValue, (val) => {
  display.value = toDisplay(val)
}, { immediate: true })

let timer: number | undefined
function handleInput(e: Event) {
  // Every time the user types, we:
  // 1) Clean the value to keep only digits and one dot
  // 2) Add commas so it’s easy to read
  // 3) Tell the parent about the clean value (optionally waiting a bit)
  const val = (e.target as HTMLInputElement).value
  // compute formatted for display
  const numeric = toModel(val)
  const formatted = formatNumberWithCommas(numeric)
  display.value = formatted
  // debounce emit to parent
  if (props.debounceMs && props.debounceMs > 0) {
    if (timer) window.clearTimeout(timer)
    timer = window.setTimeout(() => emit('update:modelValue', numeric), props.debounceMs)
  } else {
    emit('update:modelValue', numeric)
  }
}

// SIZE HELPERS
// These map the size prop to Bootstrap classes.
const sizeClass = computed(() => props.size === 'sm' ? 'input-group-sm' : props.size === 'lg' ? 'input-group-lg' : '')
const sizeClassControl = computed(() => props.size === 'sm' ? 'form-control-sm' : props.size === 'lg' ? 'form-control-lg' : '')

const placeholder = computed(() => props.placeholder ?? '0')
</script>

<style scoped>
/* No custom styles; relies on Bootstrap input-group and small size utilities. */
</style>
