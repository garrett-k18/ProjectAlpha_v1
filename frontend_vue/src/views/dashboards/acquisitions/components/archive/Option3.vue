<template>
  <!-- Option 3 card demonstrates a slide-out drawer experience for trade controls -->
  <div class="card h-100 position-relative overflow-hidden">
    <!-- Header contains the primary toggle button and contextual text -->
    <div class="card-header border-0 pb-0">
      <!-- Flex layout splits the textual context and the toggle button -->
      <div class="d-flex align-items-start justify-content-between gap-3">
        <!-- Text stack describes which prototype the viewer is observing -->
        <div>
          <!-- Subtitle clarifies the prototype number -->
          <p class="text-uppercase text-muted fw-semibold fs-6 mb-1">Slide-Out Command Drawer (Option 3)</p>
          <!-- Headline mirrors the active trade or placeholder text -->
          <h5 class="mb-0">{{ resolvedTradeName }}</h5>
          <!-- Secondary line shows the seller context for added clarity -->
          <div class="text-muted small">Seller · {{ resolvedSellerName }}</div>
        </div>
        <!-- Toggle button opens and closes the simulated drawer -->
        <button
          type="button"
          class="btn btn-sm btn-outline-primary"
          @click="toggleDrawer"
        >
          <i :class="drawerIcon"></i>
          <span class="ms-2">{{ drawerLabel }}</span>
        </button>
      </div>
    </div>

    <!-- Body holds an illustrative summary card explaining the drawer purpose -->
    <div class="card-body pt-3 pe-4">
      <!-- Summary panel gives a quick explanation of what the drawer contains -->
      <div class="border rounded-3 p-3 bg-light">
        <h6 class="fw-semibold mb-2">Command Center Summary</h6>
        <p class="mb-2 text-muted">
          {{ resolvedSummary }}
        </p>
        <ul class="list-unstyled mb-0">
          <li v-for="(item, index) in summaryBullets" :key="index" class="d-flex align-items-start gap-2 mb-1">
            <i class="mdi mdi-check-circle-outline text-success"></i>
            <span>{{ item }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Drawer panel slides in from the right side of the card -->
    <transition name="option-three-slide">
      <aside
        v-if="drawerOpen"
        class="option-three-drawer bg-body border-start"
        role="complementary"
        aria-label="Trade controls drawer"
      >
        <!-- Drawer header shows the same trade information and a close button -->
        <div class="d-flex align-items-start justify-content-between mb-3">
          <div>
            <span class="badge bg-primary-subtle text-primary-emphasis fw-semibold text-uppercase">Active</span>
            <h6 class="mt-2 mb-0">{{ resolvedTradeName }}</h6>
            <small class="text-muted">Managed by {{ resolvedSellerName }}</small>
          </div>
          <button type="button" class="btn btn-sm btn-link text-decoration-none" @click="toggleDrawer">
            Close
          </button>
        </div>
        <!-- Drawer content loops through the provided sections -->
        <div class="d-flex flex-column gap-3">
          <section v-for="section in sections" :key="section.id" class="option-three-section">
            <header class="d-flex align-items-center justify-content-between mb-2">
              <div>
                <h6 class="mb-0">{{ section.title }}</h6>
                <small class="text-muted">{{ section.subtitle }}</small>
              </div>
              <span v-if="section.badge" class="badge bg-secondary-subtle text-secondary-emphasis">{{ section.badge }}</span>
            </header>
            <div class="vstack gap-2">
              <button
                v-for="item in section.items"
                :key="item.id"
                type="button"
                class="btn btn-light border text-start w-100 d-flex justify-content-between align-items-center"
                @click="emit('trigger', item.id)"
              >
                <div class="d-flex gap-2 align-items-start">
                  <i :class="[item.icon, 'fs-5 text-primary']"></i>
                  <div class="d-flex flex-column">
                    <span class="fw-semibold">{{ item.label }}</span>
                    <small class="text-muted">{{ item.description }}</small>
                  </div>
                </div>
                <span v-if="item.badge" class="badge bg-primary-subtle text-primary-emphasis">{{ item.badge }}</span>
              </button>
            </div>
          </section>
        </div>
      </aside>
    </transition>
  </div>
</template>

<script setup lang="ts">
// Import ref and computed from Vue to manage reactive state in the drawer prototype
import { computed, ref } from 'vue' // Provides reactivity utilities for state and derived values

// Type describing the command items that live inside each drawer section
interface DrawerItem { // Defines the structure for individual control entries
  id: string // Unique identifier emitted when the item is triggered
  label: string // Human-readable name displayed in the drawer button
  description: string // Helper copy explaining the control purpose
  icon: string // Icon class string for the Material Design Icons glyph
  badge?: string | null // Optional badge text for counts or status
}

// Type describing the sections that organize drawer items into logical groups
interface DrawerSection { // Defines a drawer grouping such as "Settings" or "Documents"
  id: string // Unique identifier used for rendering keys
  title: string // Section heading shown at the top of the group
  subtitle: string // Supporting caption describing the group focus
  badge?: string | null // Optional badge showing aggregated counts for the section
  items: DrawerItem[] // Collection of actionable entries inside the section
}

// Define component props with defaults so the preview works without real data from the parent
const props = withDefaults(defineProps<{
  sellerName: string | null // Seller label to display in card and drawer
  tradeName: string | null // Trade label to display in card and drawer
  summary: string | null // Optional summary paragraph describing trade status
  sections: DrawerSection[] // Sections containing the actionable items rendered in the drawer
}>(), {
  sellerName: 'No seller selected', // Fallback seller label when no trade is active
  tradeName: 'No trade selected', // Fallback trade label when not yet chosen
  summary: 'Use this drawer to coordinate trade settings, document handling, and award approvals without leaving the dashboard.', // Default summary guidance text
  sections: () => [ // Default drawer sections showing typical acquisition workflows
    {
      id: 'settings', // Identifier for the settings group
      title: 'Settings', // Heading displayed in the drawer
      subtitle: 'Control trade assumptions and notifications.', // Subtitle clarifying the scope
      badge: 'Configured', // Badge letting users know the section is configured
      items: [ // Items under the settings bucket
        {
          id: 'settings-assumptions', // Identifier emitted when assumptions item is clicked
          label: 'Trade Assumptions', // Button label for managing assumptions
          description: 'Edit bid, settlement, and closing expectations.', // Helper text describing the action
          icon: 'mdi mdi-cog-outline', // Icon representing configuration settings
          badge: 'Auto-save' // Badge highlighting auto-save behavior
        },
        {
          id: 'settings-alerts', // Identifier for alerts item
          label: 'Alert Rules', // Button label for notifications
          description: 'Tune milestone alerts and escalation rules.', // Helper text summarizing notifications
          icon: 'mdi mdi-bell-ring-outline' // Icon representing notifications
        }
      ]
    },
    {
      id: 'documents', // Identifier for the documents group
      title: 'Documents', // Documents section heading
      subtitle: 'Centralize diligence packages and shareouts.', // Subtitle clarifying focus
      badge: '8 files', // Badge showing number of tracked documents
      items: [ // Document-related actions
        {
          id: 'documents-room', // Identifier for the document room entry
          label: 'Document Room', // Button label for the primary document area
          description: 'Review uploaded BPOs, appraisals, and legal files.', // Helper text summarizing the document room
          icon: 'mdi mdi-folder-file-outline', // Icon representing folders
          badge: 'New updates' // Badge indicating fresh uploads
        },
        {
          id: 'documents-share', // Identifier for sharing entry
          label: 'Secure Share', // Button label for share links
          description: 'Generate guest links for counterparties.', // Helper text describing share flow
          icon: 'mdi mdi-link-variant' // Icon representing link share
        }
      ]
    },
    {
      id: 'approvals', // Identifier for the approvals group
      title: 'Approvals', // Approvals section heading
      subtitle: 'Track awards and decision checkpoints.', // Subtitle clarifying the approval workflow
      badge: '2 pending', // Badge showing outstanding approvals
      items: [ // Approval related controls
        {
          id: 'approvals-checklist', // Identifier for the checklist entry
          label: 'Approval Checklist', // Button label for checklist
          description: 'Monitor outstanding diligence approvals and owners.', // Helper text summarizing the checklist
          icon: 'mdi mdi-clipboard-check-outline', // Icon representing checklist
          badge: '2 pending' // Badge indicating pending approvals
        },
        {
          id: 'approvals-awards', // Identifier for asset awards entry
          label: 'Asset Awards', // Button label for awarding assets
          description: 'Confirm award status for specific asset IDs.', // Helper text summarizing the award workflow
          icon: 'mdi mdi-trophy-award' // Icon representing awards
        }
      ]
    }
  ]
})

// Expose an event so the parent dashboard can respond when the user activates a drawer item
const emit = defineEmits<{
  (event: 'trigger', id: string): void // Emits the identifier for whichever action the user clicked
}>()

// drawerOpen tracks whether the drawer is currently visible
const drawerOpen = ref<boolean>(false) // Local state toggled by the header button

// resolvedSellerName chooses either the provided seller or the default placeholder
const resolvedSellerName = computed(() => props.sellerName ?? 'No seller selected') // Ensures UI never shows blank seller fields

// resolvedTradeName mirrors the logic for the trade headline
const resolvedTradeName = computed(() => props.tradeName ?? 'No trade selected') // Guarantees a readable trade label

// resolvedSummary prefers the provided summary or falls back to the default descriptive text
const resolvedSummary = computed(() => props.summary ?? 'Use this drawer to coordinate trade settings, document handling, and award approvals without leaving the dashboard.') // Keeps the summary paragraph populated

// summaryBullets splits the summary into key talking points for the card body list
const summaryBullets = computed(() => [ // Converts the summary concept into bullet points for clarity
  'Group settings, documents, and approvals into one command space.', // Highlights consolidated workflows
  'Surface pending counts and quick links for each trade workflow.', // Emphasizes visibility of statuses
  'Reduce clutter in the main dashboard by moving detail actions into this drawer.' // Communicates UX benefit
])

// drawerLabel returns the button copy based on the open state
const drawerLabel = computed(() => drawerOpen.value ? 'Hide Drawer' : 'Show Drawer') // Keeps the toggle button text intuitive

// drawerIcon selects an icon class matching the drawer state
const drawerIcon = computed(() => drawerOpen.value ? 'mdi mdi-chevron-right-box' : 'mdi mdi-chevron-left-box') // Provides directional feedback via iconography

// toggleDrawer switches the drawer open state between true and false
function toggleDrawer(): void { // Handles the user clicking the toggle button
  drawerOpen.value = !drawerOpen.value // Flip the boolean state controlling drawer visibility
}
</script>

<style scoped>
/* Transition classes produce a smooth slide animation for the drawer */
.option-three-slide-enter-from,
.option-three-slide-leave-to {
  transform: translateX(100%); /* Start or end off-screen to the right */
  opacity: 0; /* Fade while sliding */
}

.option-three-slide-enter-active,
.option-three-slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease; /* Animate transform and opacity simultaneously */
}

/* Drawer container sits on top of the card content without breaking layout */
.option-three-drawer {
  position: absolute; /* Position relative to the card container */
  top: 0; /* Align with top of the card */
  right: 0; /* Anchor to the right edge */
  height: 100%; /* Stretch from top to bottom for full-height drawer */
  width: 320px; /* Fixed width mimicking Hyper UI drawers */
  padding: 1.5rem; /* Comfortable interior spacing */
  box-shadow: -6px 0 24px rgba(15, 23, 42, 0.08); /* Soft shadow separating drawer from content */
  z-index: 2; /* Elevate above card body */
}

/* Section styling keeps spacing consistent inside the drawer */
.option-three-section {
  border: 1px solid rgba(148, 163, 184, 0.2); /* Light border to frame each section */
  border-radius: 0.75rem; /* Rounded corners matching Hyper UI aesthetic */
  padding: 1rem; /* Internal spacing for readability */
  background-color: rgba(248, 250, 252, 0.9); /* Subtle background to separate sections */
}
</style>
