<template>
  <!-- Card container displays Option 2 (Tabbed Control Center) next to other prototypes -->
  <div class="card h-100">
    <!-- Header houses the segmented tab navigation -->
    <div class="card-header border-0 pb-0">
      <!-- Flex wrapper keeps title and tabs aligned -->
      <div class="d-flex flex-column gap-2">
        <!-- Title label clarifies which prototype the viewer is inspecting -->
        <p class="text-uppercase text-muted fw-semibold fs-6 mb-0">Tabbed Control Center (Option 2)</p>
        <!-- Horizontal nav uses Bootstrap pills to switch between action groups -->
        <ul class="nav nav-pills gap-1" role="tablist">
          <!-- Render each tab pill with accessible aria labels -->
          <li v-for="tab in tabs" :key="tab.id" class="nav-item" role="presentation">
            <!-- Button toggles the active tab state and emits the change -->
            <button
              class="nav-link"
              :class="{ active: tab.id === activeTab }"
              type="button"
              role="tab"
              :aria-selected="tab.id === activeTab"
              @click="onTabClick(tab.id)"
            >
              {{ tab.label }}
              <span v-if="tab.badge" class="badge bg-light text-body ms-2">{{ tab.badge }}</span>
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Body shows contextual actions for the selected tab -->
    <div class="card-body pt-3">
      <!-- Tab panel wrapper mimics Hyper UI tab content spacing -->
      <div class="tab-content">
        <!-- Display a panel of card-like buttons for each action -->
        <div class="row g-2">
          <div
            v-for="action in visibleActions"
            :key="action.id"
            class="col-12"
          >
            <!-- Each action renders as a soft colored tile with icon and metadata -->
            <div class="border rounded-3 p-3 d-flex gap-3 align-items-start"
                 :class="action.surfaceClasses"
                 role="button"
                 tabindex="0"
                 @click="emit('trigger', action.id)"
                 @keydown.enter.prevent="emit('trigger', action.id)"
                 @keydown.space.prevent="emit('trigger', action.id)"
            >
              <!-- Icon container keeps glyph centered and sized consistently -->
              <div class="flex-shrink-0">
                <div class="rounded-circle bg-white shadow-sm d-flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                  <i :class="[action.icon, 'fs-4']"></i>
                </div>
              </div>
              <!-- Textual content stack -->
              <div class="flex-grow-1">
                <div class="d-flex align-items-center justify-content-between">
                  <span class="fw-semibold">{{ action.label }}</span>
                  <span v-if="action.badge" class="badge" :class="action.badgeClasses">{{ action.badge }}</span>
                </div>
                <small class="text-muted">{{ action.description }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Import computed for derived state and reactive for local tab tracking
import { computed, reactive } from 'vue' // Core Vue Composition API utilities

// TabDefinition describes the shape expected for the tab navigation items
type TabDefinition = {
  id: string // Unique identifier for the tab element
  label: string // Visible text shown on the tab pill
  badge?: string | null // Optional badge content showing counts or notes
}

// ActionDefinition describes the structure for individual action tiles
type ActionDefinition = {
  id: string // Unique identifier emitted when the tile is selected
  label: string // Title text displayed on the tile
  description: string // Supporting copy explaining what the action performs
  icon: string // Icon class string for the Material Design Icons glyph
  group: string // Tab group identifier used to filter actions per tab
  surfaceClasses: string // Tailwind/Bootstrap class string controlling tile styling
  badge?: string | null // Optional badge text surfaced at the tile level
  badgeClasses?: string | null // Optional class string customizing the badge appearance
}

// Define component props with defaults so the prototype renders meaningful content without parent data
const props = withDefaults(defineProps<{
  tabs: TabDefinition[] // Tabs rendered in the nav pills row
  actions: ActionDefinition[] // Action tiles associated with each tab group
  defaultTab: string | null // Optional identifier specifying the initial active tab
}>(), {
  tabs: () => [ // Default tabs show three primary trade workflows
    { id: 'workflow', label: 'Workflow', badge: '4' }, // Workflow tab with sample badge count
    { id: 'documents', label: 'Documents', badge: '8' }, // Documents tab with sample badge count
    { id: 'approvals', label: 'Approvals', badge: '2' } // Approvals tab with sample badge count
  ],
  actions: () => [ // Default actions populate each tab with illustrative tiles
    {
      id: 'workflow-calendar', // Identifier for timeline configuration tile
      label: 'Bid Timeline', // Tile title text for timeline adjustments
      description: 'Adjust bid submission and settlement milestones.', // Helper copy describing the tile purpose
      icon: 'mdi mdi-calendar-clock-outline', // Icon representing scheduling utilities
      group: 'workflow', // Associates this tile with the workflow tab
      surfaceClasses: 'bg-info-subtle text-info-emphasis border-info-subtle', // Styling classes for the tile surface
      badge: 'Auto-save', // Badge text indicating automatic persistence
      badgeClasses: 'bg-info text-white' // Badge styling for informational emphasis
    },
    {
      id: 'workflow-notes', // Identifier for the notes tile
      label: 'Deal Notes', // Tile title for meeting notes capture
      description: 'Centralize context from diligence meetings.', // Helper copy describing note aggregation
      icon: 'mdi mdi-notebook-edit-outline', // Icon representing note taking
      group: 'workflow', // Associates this tile with the workflow tab
      surfaceClasses: 'bg-info-subtle text-info-emphasis border-info-subtle' // Styling classes for consistent appearance
    },
    {
      id: 'documents-room', // Identifier for the documents room tile
      label: 'Document Room', // Tile title highlighting document management
      description: 'Access diligence folders and document statuses.', // Helper copy describing document access
      icon: 'mdi mdi-folder-file-outline', // Icon representing file folders
      group: 'documents', // Associates this tile with the documents tab
      surfaceClasses: 'bg-primary-subtle text-primary-emphasis border-primary-subtle', // Styling classes for the tile surface
      badge: '8 files', // Badge representing number of tracked files
      badgeClasses: 'bg-primary text-white' // Badge styling aligning with primary emphasis
    },
    {
      id: 'documents-share', // Identifier for the share link tile
      label: 'Share Link', // Tile title highlighting sharing controls
      description: 'Generate restricted links for counterparties.', // Helper copy describing secure sharing
      icon: 'mdi mdi-link-variant', // Icon representing link sharing
      group: 'documents', // Associates this tile with the documents tab
      surfaceClasses: 'bg-primary-subtle text-primary-emphasis border-primary-subtle' // Styling classes for the tile surface
    },
    {
      id: 'approvals-progress', // Identifier for the approvals checklist tile
      label: 'Approval Checklist', // Tile title referencing approvals tracking
      description: 'Monitor buy-side approvals and assign owners.', // Helper copy describing approval workflows
      icon: 'mdi mdi-check-decagram-outline', // Icon representing completed actions
      group: 'approvals', // Associates this tile with the approvals tab
      surfaceClasses: 'bg-warning-subtle text-warning-emphasis border-warning-subtle', // Styling classes for the tile surface
      badge: '2 pending', // Badge highlighting number of outstanding approvals
      badgeClasses: 'bg-warning text-dark' // Badge styling aligning with warning emphasis
    },
    {
      id: 'approvals-awards', // Identifier for the asset awards tile
      label: 'Asset Awards', // Tile title referencing award operations
      description: 'Approve awarded asset IDs and notify sellers.', // Helper copy describing award workflow
      icon: 'mdi mdi-trophy-award', // Icon representing awards and recognition
      group: 'approvals', // Associates this tile with the approvals tab
      surfaceClasses: 'bg-warning-subtle text-warning-emphasis border-warning-subtle' // Styling classes for the tile surface
    }
  ],
  defaultTab: 'workflow' // Default active tab ensures workflow content appears first
})

// Local reactive state tracks which tab is active across the prototype
const state = reactive({
  activeTab: props.defaultTab ?? (props.tabs[0]?.id ?? null) // Initialize active tab from prop or fall back to first tab id
})

// Emits allow the parent dashboard to react when tabs change or actions fire
const emit = defineEmits<{
  (event: 'tab-change', tabId: string | null): void // Emits whenever the active tab changes
  (event: 'trigger', actionId: string): void // Emits whenever an action tile is selected
}>()

// activeTab computed getter exposes the current tab id to the template and other computed helpers
const activeTab = computed(() => state.activeTab) // Keeps template bindings reactive to tab changes

// visibleActions filters the provided actions by the current tab group
const visibleActions = computed(() => {
  return props.actions.filter(action => action.group === activeTab.value) // Return actions whose group matches active tab id
})

// onTabClick updates the active tab and emits the tab-change event for analytics
function onTabClick(id: string) {
  state.activeTab = id // Update local reactive state with the newly selected tab id
  emit('tab-change', id) // Notify the parent component about the tab change
}
</script>
