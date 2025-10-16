<template>
  <!-- Root card wraps the entire Option 1 (Action Dock) concept so it can sit inside dashboard columns -->
  <div class="card h-100">
    <!-- Header communicates which trade is being summarized and highlights the status badge -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <!-- Heading matches TradeTasking typography for visual consistency -->
      <h4 class="header-title mb-0">Actions</h4>
      <!-- Status badge gives at-a-glance health indicator -->
      <span class="badge" :class="badgeClasses">{{ resolvedStatus }}</span>
    </div>

    <!-- Body lists each primary action in a vertical stack of wide buttons -->
    <div class="card-body pt-3">
      <!-- Stack keeps spacing consistent between action buttons -->
      <div class="vstack gap-2">
        <!-- Each button is full-width, text-aligned to the left, and triggers the emit when clicked -->
        <button
          v-for="action in actionItems"
          :key="action.id"
          type="button"
          class="btn text-start w-100 d-flex align-items-start justify-content-between"
          :class="action.buttonClasses"
          @click="emit('trigger', action.id)"
        >
          <!-- Block showing icon and text information -->
          <div class="d-flex align-items-start gap-2">
            <!-- Icon uses Material Design Icons classes passed from the parent -->
            <i :class="[action.icon, 'fs-4']"></i>
            <!-- Text stack for label and description copy -->
            <div class="d-flex flex-column">
              <!-- Label is bold so the action is easy to skim -->
              <span class="fw-semibold">{{ action.label }}</span>
              <!-- Description explains exactly what happens when the button is used -->
              <small class="text-muted">{{ action.description }}</small>
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

// Type alias for acceptable badge color variants to keep class generation consistent
type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'secondary' // Restricts badges to known themes

// Define the props with defaults so the component displays meaningful placeholders when the parent has no selection yet
const props = withDefaults(defineProps<{
  sellerName: string | null // Prop for the seller label in the subtitle
  tradeName: string | null // Prop for the trade label in the title
  statusLabel: string | null // Prop for the status badge text
  statusVariant: BadgeVariant | null // Prop controlling the badge color
  actionItems: Array<{ // Prop listing the actionable buttons
    id: string // Unique identifier for the button event payload
    label: string // Button title shown to the user
    description: string // Helper description under the title
    icon: string // Material Design Icon class string
    buttonClasses: string // Styling classes applied to the button shell
    badge?: string | null // Optional badge text such as counts
    badgeClasses?: string | null // Optional badge color classes
  }>
}>(), {
  sellerName: 'No seller selected', // Default seller placeholder copy
  tradeName: 'No trade selected', // Default trade placeholder copy
  statusLabel: 'No status', // Default status placeholder copy
  statusVariant: 'secondary', // Default badge palette selection
  actionItems: () => [ // Default actions illustrate layout without wiring
    {
      id: 'assumptions', // Identifier for emitting trade assumptions action
      label: 'Trade Assumptions', // Button label for assumptions block
      description: 'Review bid and settlement timing assumptions.', // Helper text summarizing the action
      icon: 'mdi mdi-cog-outline', // Icon referencing the cog outline glyph
      buttonClasses: 'btn btn-light border', // Button styling using light surface with border
      badge: 'Auto-Save', // Badge text indicating auto-save behavior
      badgeClasses: 'bg-info-subtle text-info-emphasis' // Badge colors aligning with informational tone
    },
    {
      id: 'documents', // Identifier for emitting documents action
      label: 'Documents Vault', // Button label for document management
      description: 'Manage diligence packages and shared artifacts.', // Helper text summarizing the documents workflow
      icon: 'mdi mdi-file-table-box-multiple', // Icon referencing document stack glyph
      buttonClasses: 'btn btn-light border', // Button styling consistent across examples
      badge: '8 items', // Badge text hinting at document counts
      badgeClasses: 'bg-primary text-white' // Badge colors aligning with primary emphasis
    },
    {
      id: 'approvals', // Identifier for emitting approvals action
      label: 'Approval Center', // Button label for approvals workflow
      description: 'Track pending approvals and award asset IDs.', // Helper text summarizing approvals responsibilities
      icon: 'mdi mdi-shield-check-outline', // Icon referencing shield check glyph
      buttonClasses: 'btn btn-light border', // Button styling consistent for visual rhythm
      badge: '2 pending', // Badge text communicating outstanding approvals
      badgeClasses: 'bg-warning text-dark' // Badge colors aligning with cautionary tone
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

// computed helper figures out which badge text to show
const resolvedStatus = computed(() => props.statusLabel ?? 'No status') // Keeps badge text synchronized with prop

// computed helper builds the badge class string from the selected variant
const badgeClasses = computed(() => {
  const variantMap: Record<BadgeVariant, string> = { // Map variants to Bootstrap utility classes
    primary: 'bg-primary text-white', // Primary styling for high emphasis states
    success: 'bg-success text-white', // Success styling for completion states
    warning: 'bg-warning text-dark', // Warning styling for pending attention states
    danger: 'bg-danger text-white', // Danger styling for blocking issues
    secondary: 'bg-secondary text-white' // Secondary styling for neutral states
  }
  const key = props.statusVariant ?? 'secondary' // Choose provided variant or default to secondary
  return variantMap[key] // Return the resolved class string
})
</script>
