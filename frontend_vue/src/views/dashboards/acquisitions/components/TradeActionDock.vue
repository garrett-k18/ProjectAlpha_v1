<template>
  <!-- Root card wraps the entire Option 1 (Action Dock) concept so it can sit inside dashboard columns -->
  <div class="card h-100">
    <!-- Header communicates which trade is being summarized and includes status selector -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <!-- Heading matches TradeTasking typography for visual consistency -->
      <h4 class="header-title mb-0">Actions</h4>
      <!-- Status selector allows users to update trade lifecycle directly from the dock -->
      <div class="d-flex align-items-center gap-2" role="group" aria-label="Trade status controls">
        <select
          class="form-select form-select-sm"
          :value="currentStatus"
          :disabled="savingStatus"
          @change="handleStatusChange"
        >
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <button
          class="btn btn-sm btn-outline-secondary"
          type="button"
          :disabled="savingStatus"
          @click="refreshStatus"
        >
          <i class="mdi mdi-refresh"></i>
        </button>
      </div>
    </div>

    <!-- Body lists each primary action in a vertical stack of wide buttons -->
    <div class="card-body pt-3">
      <!-- Stack keeps spacing consistent between action buttons -->
      <div class="vstack gap-2">
        <!-- Each button is full-width, text-aligned to the left, and triggers the emit when clicked -->
        <button
          v-for="action in resolvedActionItems"
          :key="action.id"
          type="button"
          class="btn text-start w-100 d-flex align-items-center justify-content-between"
          :class="action.buttonClasses"
          @click="emit('trigger', action.id)"
        >
          <!-- Block showing icon and text information -->
          <div class="d-flex align-items-center gap-2">
            <!-- Icon uses Material Design Icons classes passed from the parent -->
            <i :class="[action.icon, 'fs-4']"></i>
            <!-- Text stack for label and description copy -->
            <div class="d-flex flex-column">
              <!-- Label is bold so the action is easy to skim -->
              <span class="fw-semibold">{{ action.label }}</span>
              <!-- Description explains exactly what happens when the button is used -->
              <small v-if="action.description" class="text-muted">{{ action.description }}</small>
            </div>
          </div>
          <!-- Optional badge mirrors Hyper UI chips to show counts or state -->
          <span
            v-if="action.badge"
            class="badge ms-2 align-self-center"
            :class="action.badgeClasses"
          >
            {{ action.badge }}
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import computed for building derived strings from the incoming props
import { computed } from 'vue' // Provides reactive memoization helpers

// Define the props with defaults so the component displays meaningful placeholders when the parent has no selection yet
const props = withDefaults(defineProps<{
  sellerName: string | null // Prop for the seller label in the subtitle
  tradeName: string | null // Prop for the trade label in the title
  statusValue: string | null
  statusOptions: Array<{ value: string; label: string }>
  savingStatus: boolean
  onUpdateStatus?: (newStatus: string) => Promise<void> | void
  onRefreshStatus?: () => Promise<void> | void
  hasActiveTrade?: boolean
  actionItems?: Array<{ // Prop listing the actionable buttons
    id: string // Unique identifier for the button event payload
    label: string // Button title shown to the user
    description: string | null // Helper description under the title
    icon: string // Material Design Icon class string
    buttonClasses: string // Styling classes applied to the button shell
    badge?: string | null // Optional badge text such as counts
    badgeClasses?: string | null // Optional badge color classes
  }>
}>(), {
  sellerName: 'No seller selected', // Default seller placeholder copy
  tradeName: 'No trade selected', // Default trade placeholder copy
  statusValue: null,
  statusOptions: () => [
    { value: 'PASS', label: 'Pass' },
    { value: 'DD', label: 'Due Diligence' },
    { value: 'AWARDED', label: 'Awarded' },
    { value: 'BOARD', label: 'Boarded' },
    { value: 'ARCHIVE', label: 'Archive' }
  ],
  savingStatus: false,
  hasActiveTrade: false,
  actionItems: () => [ // Default actions illustrate layout without wiring
    {
      id: 'trade-assumptions', // Identifier for emitting trade assumptions action
      label: 'Trade Assumptions', // Button label for assumptions block
      description: null, // Helper text summarizing the action
      icon: 'mdi mdi-cog-outline', // Icon referencing the cog outline glyph
      buttonClasses: 'btn btn-light border', // Button styling using light surface with border
      badge: null, // Badge text placeholder showing no highlight by default for the assumptions action
      badgeClasses: null // Badge colors placeholder that keeps the badge visually hidden when badge is null
    },
    {
      id: 'trade-documents', // Identifier for emitting documents action
      label: 'Trade Documents', // Button label for document management
      description: null, // Helper text summarizing the documents workflow
      icon: 'mdi mdi-file-table-box-multiple', // Icon referencing document stack glyph
      buttonClasses: 'btn btn-light border', // Button styling consistent across examples
      badge: '8 items', // Badge text hinting at document counts
      badgeClasses: 'bg-primary text-white' // Badge colors aligning with primary emphasis
    },
    {
      id: 'trade-approvals', // Identifier for emitting approvals action
      label: 'Approval Center', // Button label for approvals workflow
      description: null, // Helper text summarizing approvals responsibilities
      icon: 'mdi mdi-shield-check-outline', // Icon referencing shield check glyph
      buttonClasses: 'btn btn-light border', // Button styling consistent for visual rhythm
      badge: null, // Badge text placeholder showing no highlight until a trade is active
      badgeClasses: null // Badge colors placeholder that keeps the badge visually hidden when badge is null
    }
  ]
})

// Define the event emitter so the parent can respond to button clicks
const emit = defineEmits<{
  (event: 'trigger', id: string): void // Emits trigger event with the action identifier
}>()

// computed helper returns a readable seller name by falling back to the default placeholder
const resolvedSellerName = computed(() => props.sellerName ?? 'No seller selected') // Ensures subtitle always renders text

// computed helper returns a readable trade name with the same fallback behavior
const resolvedTradeName = computed(() => props.tradeName ?? 'No trade selected') // Ensures title always renders text

// computed helper figures out which status value to show
const currentStatus = computed(() => props.statusValue ?? 'DD')

const onStatusChange = async (value: string) => {
  if (props.onUpdateStatus) {
    await props.onUpdateStatus(value)
  }
}

const refreshStatus = async () => {
  if (props.onRefreshStatus) {
    await props.onRefreshStatus()
  }
}

const handleStatusChange = async (event: Event) => {
  const target = event.target as HTMLSelectElement | null
  if (!target) {
    return
  }
  await onStatusChange(target.value)
}

const resolvedActionItems = computed(() => {
  return props.actionItems.map((item) => {
    if (item.id === 'trade-assumptions') {
      return {
        ...item,
        badge: props.hasActiveTrade ? 'Auto-Save' : null,
        badgeClasses: props.hasActiveTrade ? 'bg-info-subtle text-info-emphasis' : null,
      }
    }
    if (item.id === 'trade-approvals') {
      return {
        ...item,
        badge: props.hasActiveTrade ? '2 pending' : null,
        badgeClasses: props.hasActiveTrade ? 'bg-warning text-dark' : null,
      }
    }
    return item
  })
})
</script>
