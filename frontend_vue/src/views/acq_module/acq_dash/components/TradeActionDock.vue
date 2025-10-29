<template>
  <!-- Root card wraps the entire Option 1 (Action Dock) concept so it can sit inside dashboard columns -->
  <div class="card h-100">
    <!-- Header keeps visual hierarchy light now that the status control lives in the body -->
    <div class="d-flex card-header justify-content-between align-items-center py-2">
      <h4 class="header-title m-1">Actions</h4>
    </div>

    <!-- Confirmation modal appears when high-impact statuses (Pass/Board) are chosen -->
    <BModal
      v-model="showStatusConfirm"
      :title="confirmCopy.title"
      centered
      hide-header-close
      dialog-class="trade-status-confirm"
    >
      <p class="mb-3">{{ confirmCopy.body }}</p>
      <ul class="mb-3 ps-3">
        <li v-for="note in confirmCopy.notes" :key="note">{{ note }}</li>
      </ul>
      <template #footer>
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-outline-secondary" type="button" @click="cancelStatusChange">
            Cancel
          </button>
          <button
            class="btn"
            type="button"
            :class="confirmCopy.confirmButtonClass"
            @click="confirmStatusChange"
          >
            {{ confirmCopy.confirmLabel }}
          </button>
        </div>
      </template>
    </BModal>

    <!-- Body lists each primary action in a vertical stack of wide buttons -->
    <div class="card-body pt-3">
      <!-- Stack keeps spacing consistent between action buttons -->
      <div class="vstack gap-2">
        <!-- Trade status sits in its own control card so it visually aligns with action buttons -->
        <div
          class="status-card btn text-start w-100 d-flex align-items-center justify-content-between btn-light border"
          role="group"
          aria-label="Trade status controls"
        >
          <div class="d-flex align-items-center gap-2">
            <i class="mdi mdi-flag-outline fs-4"></i>
            <div class="d-flex flex-column">
              <span class="fw-semibold">Trade Status</span>
            </div>
          </div>
          <select
            class="form-select form-select-sm status-select"
            v-model="selectedStatus"
            :disabled="savingStatus"
            @change="handleStatusChange"
          >
            <option v-for="option in decoratedStatusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
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
// Import computed for building derived strings, ref for local state, and watch for synchronization
import { computed, ref, watch } from 'vue' // Provides reactive memoization helpers and reactive primitives
// Import BootstrapVue Next modal for confirmation workflow (Docs: https://bootstrap-vue-next.github.io/components/modal/)
import { BModal } from 'bootstrap-vue-next'

// Define the props with defaults so the component displays meaningful placeholders when the parent has no selection yet
const props = withDefaults(defineProps<{
  sellerName: string | null // Prop for the seller label in the subtitle
  tradeName: string | null // Prop for the trade label in the title
  statusValue: string | null
  statusOptions: Array<{ value: string; label: string }>
  savingStatus: boolean
  onUpdateStatus?: (newStatus: string) => Promise<boolean | void> | boolean | void
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
    { value: 'INDICATIVE', label: 'Indicative' },
    { value: 'DD', label: 'Due Diligence' },
    { value: 'AWARDED', label: 'Awarded' },
    { value: 'BOARD', label: 'Boarded' },
    { value: 'PASS', label: 'Pass' },
  ],
  savingStatus: false,
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
      label: 'Documents', // Button label for documents action
      description: null, // Helper description placeholder for document workflows
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
  ],
  hasActiveTrade: false,
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
const currentStatus = computed(() => props.statusValue ?? 'INDICATIVE')

// local ref maintains UI selection immediately while backend request finalizes
const selectedStatus = ref(currentStatus.value) // Tracks dropdown selection for immediate UX feedback
const lastCommittedStatus = ref(currentStatus.value) // Tracks last saved status so cancel can revert
const pendingStatus = ref<string | null>(null) // Holds status awaiting user confirmation
const showStatusConfirm = ref(false) // Controls visibility of confirmation modal

// keep local selection aligned with upstream prop updates (e.g., when store resolves new status)
watch(currentStatus, (value) => {
  selectedStatus.value = value
  lastCommittedStatus.value = value
})

const onStatusChange = async (value: string) => {
  if (props.onUpdateStatus) {
    const result = await props.onUpdateStatus(value)
    return result
  }
  return true
}

// Map high-impact statuses to confirmation copy so UX communicates downstream effects clearly
const confirmationCopy = {
  PASS: {
    title: 'Archive Trade?',
    body: 'Passing on this trade will archive it and remove it from the acquisitions dashboard.',
    confirmLabel: 'Yes, Archive Trade',
    confirmButtonClass: 'btn-danger',
    notes: [
      'All associated assets will no longer appear in acquisitions workflows.',
      'You can restore the trade later from the trade management section if required.',
    ],
  },
  BOARD: {
    title: 'Move Trade to Asset Management?',
    body: 'Boarding a trade promotes it into the asset management module.',
    confirmLabel: 'Yes, Move to Asset Management',
    confirmButtonClass: 'btn-success',
    notes: [
      'All assets will transition to post-acquisition workflows.',
      'Tasking and reporting will switch to asset management dashboards.',
    ],
  },
} as const

const confirmCopy = computed(() => {
  const key = pendingStatus.value as keyof typeof confirmationCopy | null
  if (!key) {
    return {
      title: 'Confirm Status Change',
      body: 'Are you sure you want to change the trade status?',
      confirmLabel: 'Confirm',
      confirmButtonClass: 'btn-primary',
      notes: [] as string[],
    }
  }
  return confirmationCopy[key]
})

const requiresConfirmation = (status: string) => ['PASS', 'BOARD'].includes(status)

const handleStatusChange = async () => {
  const next = selectedStatus.value
  if (!next) {
    return
  }
  if (requiresConfirmation(next)) {
    pendingStatus.value = next
    selectedStatus.value = lastCommittedStatus.value
    showStatusConfirm.value = true
    return
  }
  await commitStatusChange(next)
}

const resolvedActionItems = computed(() => {
  return props.actionItems.map((item) => {
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

const decoratedStatusOptions = computed(() => {
  return props.statusOptions.map((option) => {
    if (option.value === 'PASS') {
      return { ...option, label: 'Pass' }
    }
    if (option.value === 'BOARD') {
      return { ...option, label: 'Board' }
    }
    if (option.value === 'INDICATIVE') {
      return { ...option, label: 'Indicative (Initial)' }
    }
    return option
  })
})

const commitStatusChange = async (status: string) => {
  try {
    const result = await onStatusChange(status)
    if (result === false) {
      selectedStatus.value = lastCommittedStatus.value
      return
    }
    lastCommittedStatus.value = status
    selectedStatus.value = status
  } catch (error) {
    console.error('[TradeActionDock] commitStatusChange failed', error)
    selectedStatus.value = lastCommittedStatus.value
  }
}

const confirmStatusChange = async () => {
  const next = pendingStatus.value
  pendingStatus.value = null
  showStatusConfirm.value = false
  if (!next) {
    return
  }
  await commitStatusChange(next)
}

const cancelStatusChange = () => {
  pendingStatus.value = null
  showStatusConfirm.value = false
  selectedStatus.value = lastCommittedStatus.value
}
</script>

<style scoped>
.status-card {
  padding: 0.5rem 0.75rem;
  /* WHAT: match Bootstrap button vertical rhythm so card aligns with neighbors */
  /* WHY: dropdown control was adding extra space compared to standard action buttons */
  /* HOW: use same padding scale as .btn plus slight wiggle room for the select */
  min-height: auto;
}

.status-select {
  /* WHAT: restrict width so "Trade Status" heading stays on a single line while keeping options legible */
  /* WHY: user requested narrower control to preserve single-line layout */
  /* HOW: clamp width range and prevent flexbox from stretching the control */
  min-width: 140px;
  max-width: 160px;
  width: 100%;
  flex: 0 0 auto;
  border-radius: 0.5rem;
}
</style>
