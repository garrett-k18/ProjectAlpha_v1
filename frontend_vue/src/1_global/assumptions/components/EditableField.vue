<template>
  <!--
    EditableField.vue
    - Inline editable field that shows blue underlined text when not editing
    - Becomes an input field when clicked
    - Supports number, text, percentage, and currency formats
    
    Usage:
    <EditableField
      :value="state.fcStateMonths"
      @update="state.fcStateMonths = $event"
      type="number"
      :min="0"
      :step="1"
    />
  -->
  <div class="editable-field-wrapper" @click.stop="startEditing" v-if="!isEditing">
    <span class="editable-text">{{ displayValue }}</span>
  </div>
  <div class="editable-field-wrapper" v-else @click.stop>
    <input
      ref="inputRef"
      :type="type"
      :value="editValue"
      @input="handleInput"
      @blur="finishEditing"
      @keyup.enter="finishEditing"
      @keyup.esc="cancelEditing"
      :min="min"
      :max="max"
      :step="step"
      :placeholder="placeholder"
      class="editable-input"
    />
    <span v-if="suffix" class="editable-suffix">{{ suffix }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

interface Props {
  value: number | string | null | undefined
  type?: 'number' | 'text'
  min?: number
  max?: number
  step?: number
  placeholder?: string
  suffix?: string
  formatValue?: (val: number | string | null | undefined) => string
  parseValue?: (val: string) => number | string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  formatValue: undefined,
  parseValue: undefined
})

const emit = defineEmits<{
  (e: 'update', value: number | string): void
}>()

const isEditing = ref(false)
const editValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

// Display value when not editing
const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) {
    return props.placeholder || '—'
  }
  
  if (props.formatValue) {
    return props.formatValue(props.value)
  }
  
  return String(props.value)
})

// Start editing - convert display value back to raw value for input
function startEditing() {
  isEditing.value = true
  
  // Set initial edit value - use formatted value for display in input
  if (props.formatValue && props.value !== null && props.value !== undefined) {
    // Show formatted value in input (e.g., "0.63" for percentage)
    editValue.value = props.formatValue(props.value)
  } else {
    editValue.value = props.value !== null && props.value !== undefined ? String(props.value) : ''
  }
  
  // Focus input after it's rendered
  nextTick(() => {
    inputRef.value?.focus()
    inputRef.value?.select()
  })
}

// Handle input changes
function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  editValue.value = target.value
}

// Finish editing and emit update
function finishEditing() {
  if (props.parseValue) {
    const parsed = props.parseValue(editValue.value)
    emit('update', parsed)
  } else if (props.type === 'number') {
    const num = parseFloat(editValue.value)
    emit('update', isNaN(num) ? 0 : num)
  } else {
    emit('update', editValue.value)
  }
  
  isEditing.value = false
}

// Cancel editing without saving
function cancelEditing() {
  isEditing.value = false
  editValue.value = ''
}
</script>

<style scoped>
.editable-field-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-width: 60px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background-color 0.15s ease;
}

.editable-field-wrapper:hover {
  background-color: rgba(13, 110, 253, 0.05);
}

.editable-text {
  color: #0d6efd;
  text-decoration: underline;
  text-decoration-color: rgba(13, 110, 253, 0.5);
  text-underline-offset: 2px;
  cursor: pointer;
  user-select: none;
}

.editable-suffix {
  margin-left: 4px;
  color: #6c757d;
  font-size: 0.875rem;
}

.editable-input {
  width: 100%;
  border: 1px solid #0d6efd;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 0.875rem;
  outline: none;
}

.editable-input:focus {
  border-color: #0a58ca;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}
</style>
