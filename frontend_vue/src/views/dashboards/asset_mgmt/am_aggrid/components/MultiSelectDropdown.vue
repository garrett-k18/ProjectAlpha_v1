<template>
  <div class="dropdown" style="position: relative;">
    <button
      class="btn btn-sm btn-outline-secondary dropdown-toggle"
      type="button"
      @click="toggleDropdown"
      style="min-width: 120px;"
    >
      {{ label }}{{ selectedCount > 0 ? ` (${selectedCount})` : '' }}
    </button>
    <div
      v-if="isOpen"
      class="dropdown-menu show p-2"
      style="max-height: 300px; overflow-y: auto; min-width: 200px;"
      @click.stop
    >
      <div v-for="option in options" :key="option" class="form-check">
        <input
          class="form-check-input"
          type="checkbox"
          :id="`${dropdownId}-${option}`"
          :value="option"
          :checked="isSelected(option)"
          @change="handleChange(option)"
        />
        <label class="form-check-label small" :for="`${dropdownId}-${option}`">
          {{ option }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string                    // Display label (e.g., "Trade", "Seller")
  options: string[]                // Available options to select from
  modelValue: string[]             // Selected values (v-model binding)
  isOpen: boolean                  // Dropdown open state
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'update:isOpen': [value: boolean]
  'change': []                     // Emitted when selection changes
}>()

// Generate unique ID for checkbox inputs
const dropdownId = computed(() => `dropdown-${props.label.toLowerCase().replace(/\s+/g, '-')}`)

const selectedCount = computed(() => props.modelValue.length)

function isSelected(option: string): boolean {
  return props.modelValue.includes(option)
}

function handleChange(option: string): void {
  const newValue = isSelected(option)
    ? props.modelValue.filter(v => v !== option)
    : [...props.modelValue, option]

  emit('update:modelValue', newValue)
  emit('change')
}

function toggleDropdown(): void {
  emit('update:isOpen', !props.isOpen)
}
</script>

<style scoped>
/* No additional styles needed - inherits from parent */
</style>
