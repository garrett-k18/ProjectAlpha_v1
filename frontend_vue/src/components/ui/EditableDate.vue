<template>
  <!-- 
    Editable Date Component
    
    Usage: <EditableDate :value="dateString" @update="handleDateChange" />
    Currently used in: AM Module.Asset tasking sub task Task Start Dates
    - FC
    - Modification
    - Short Sale
    - Dil
    - REO

    Features:
    - Inline date picker (no visible calendar icon)
    - Click on date text to open picker
    - Styled with underline to indicate editability
    - Customizable color via CSS variable or prop
  -->
  <input 
    type="date" 
    :value="modelValue" 
    @change="handleChange"
    @click="openPicker"
    class="editable-date"
    :class="colorClass"
    :title="title"
  />
</template>

<script setup lang="ts">
import { withDefaults, defineProps, defineEmits } from 'vue'

// Props interface
interface Props {
  modelValue: string | null  // ISO date string (YYYY-MM-DD) or null
  title?: string              // Tooltip text
  colorClass?: string         // Optional custom color class (default: text-primary)
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  title: 'Click to edit date',
  colorClass: 'text-primary'
})

// Define emits for v-model support
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// Handle date change event
function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

// Open the date picker when clicking on the date text
function openPicker(event: Event) {
  const target = event.target as HTMLInputElement
  try {
    target.showPicker()
  } catch (err) {
    // showPicker() not supported in some browsers, fallback to native behavior
    console.debug('showPicker() not supported, using native date input behavior')
  }
}
</script>

<style scoped>
/* Base styling for editable date input */
.editable-date {
  /* Remove default input styling */
  border: 0;
  background: transparent;
  padding: 0;
  margin: 0;
  
  /* Make it look like inline text */
  font-size: inherit;
  font-family: inherit;
  line-height: inherit;
  width: auto;
  
  /* Indicate interactivity */
  cursor: pointer;
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  
  /* Default blue color (can be overridden with colorClass prop) */
  color: var(--editable-date-color, #0d6efd);
}

/* Hide the calendar icon - picker opens via @click handler */
.editable-date::-webkit-calendar-picker-indicator {
  display: none;
  -webkit-appearance: none;
}

.editable-date::-moz-calendar-picker-indicator {
  display: none;
}

/* Focus state for accessibility */
.editable-date:focus {
  outline: 2px solid currentColor;
  outline-offset: 2px;
  border-radius: 2px;
}

/* Hover state */
.editable-date:hover {
  opacity: 0.8;
}
</style>
