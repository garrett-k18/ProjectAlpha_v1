<template>
  <!-- 
    Editable Date Component
    
    Usage: <EditableDate :model-value="dateString" @update:model-value="handleDateChange" />
    Currently used in: AM Module.Asset tasking sub task Task Start Dates
    - FC
    - Modification
    - Short Sale
    - Dil
    - REO
    - Note Sale

    Features:
    - Clean placeholder text when empty (no ugly mm/dd/yyyy)
    - Shows formatted date when populated
    - Click to open native date picker
    - Styled with underline to indicate editability
    - Consistent blue color
  -->
  <div class="editable-date-wrapper" @click.stop="openPicker">
    <!-- WHAT: Display layer showing formatted date or placeholder -->
    <!-- WHY: Native date inputs show ugly mm/dd/yyyy, we want clean text -->
    <!-- NOTE: @click.stop prevents event from bubbling to parent (e.g., card collapse/expand) -->
    <span 
      class="editable-date-display"
      :class="[colorClass, { 'is-empty': !modelValue }]"
      :title="title"
    >
      {{ displayText }}
    </span>
    
    <!-- WHAT: Hidden native date input for picker functionality -->
    <!-- WHY: Leverage browser's native date picker UX -->
    <input 
      ref="dateInput"
      type="date" 
      :value="modelValue || ''" 
      @change="handleChange"
      class="editable-date-input"
      aria-hidden="true"
      tabindex="-1"
    />
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, defineEmits, computed, ref } from 'vue'

// Props interface
interface Props {
  modelValue: string | null  // ISO date string (YYYY-MM-DD) or null
  title?: string              // Tooltip text
  colorClass?: string         // Optional custom color class (default: text-primary)
  placeholder?: string        // Text to show when empty (default: "Select date")
}

// Define props with defaults
const props = withDefaults(defineProps<Props>(), {
  title: 'Click to edit date',
  colorClass: 'text-primary',
  placeholder: 'Select Date'
})

// Define emits for v-model support
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

// Reference to the hidden input
const dateInput = ref<HTMLInputElement | null>(null)

// WHAT: Computed display text - shows formatted date or placeholder
// WHY: Native date inputs show mm/dd/yyyy which looks unprofessional
// HOW: Format ISO date to locale string, or show placeholder when empty
const displayText = computed(() => {
  if (!props.modelValue) {
    return props.placeholder
  }
  
  try {
    // WHAT: Parse ISO date and format for display
    // WHY: Show user-friendly date format (e.g., "Nov 5, 2025" or "11/5/2025")
    const date = new Date(props.modelValue)
    // Use short date format (e.g., "11/5/2025")
    return date.toLocaleDateString('en-US', { 
      month: 'numeric', 
      day: 'numeric', 
      year: 'numeric' 
    })
  } catch {
    // Fallback to raw value if parsing fails
    return props.modelValue
  }
})

// Handle date change event
function handleChange(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

// Open the date picker when clicking on the display text
function openPicker() {
  if (!dateInput.value) return
  try {
    dateInput.value.showPicker()
  } catch (err) {
    // showPicker() not supported in some browsers, fallback to click
    dateInput.value.click()
  }
}
</script>

<style scoped>
/* WHAT: Wrapper for the editable date display */
/* WHY: Container for positioning and interaction */
.editable-date-wrapper {
  display: inline-block;
  position: relative;
  cursor: pointer;
}

/* WHAT: Visible display text (formatted date or placeholder) */
/* WHY: Show clean text instead of ugly mm/dd/yyyy placeholder */
.editable-date-display {
  /* Make it look like inline text */
  font-size: inherit;
  font-family: inherit;
  line-height: inherit;
  
  /* Indicate interactivity with underline */
  text-decoration: underline;
  text-decoration-style: dotted;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
  
  /* Default to primary blue color */
  color: var(--bs-primary, #0d6efd);
  
  /* Smooth transition on hover */
  transition: opacity 0.2s ease;
}

/* WHAT: Empty state styling */
/* WHY: Make placeholder text slightly muted */
.editable-date-display.is-empty {
  font-style: italic;
  opacity: 0.7;
}

/* WHAT: Hover state for better UX */
/* WHY: Visual feedback that element is clickable */
.editable-date-wrapper:hover .editable-date-display {
  opacity: 0.7;
}

/* WHAT: Hidden native date input */
/* WHY: We only use it for the picker, not for display */
.editable-date-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 1px;
  height: 1px;
}
</style>
