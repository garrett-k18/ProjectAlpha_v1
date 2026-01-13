<template>
  <!--
    Narrative Tab: The Loan's Story
    WHAT: Aggregates all qualitative data (notes, emails, tasks, events) into a chronological narrative.
    WHY: Provides a holistic, easy-to-follow story of the loan's lifecycle and activities.
    HOW: Fetches data from multiple sources, combines into timeline, presents as visual story feed.
  -->
  <div class="narrative-tab px-2 py-2">
    <!-- Filter Controls at Top -->
    <div class="filter-section card mb-2">
      <div class="card-body p-2">
        <div class="d-flex flex-wrap align-items-center gap-2">
          <span class="text-muted small me-2">
            <i class="ri-filter-line me-1"></i>Filter by:
          </span>
          <button
            v-for="filter in eventFilters"
            :key="filter.type"
            class="btn btn-sm"
            :class="activeFilters.includes(filter.type) ? 'btn-primary' : 'btn-outline-secondary'"
            @click="toggleFilter(filter.type)"
          >
            <i :class="filter.icon" class="me-1"></i>
            {{ filter.label }}
            <span class="badge bg-light text-dark ms-1">{{ filter.count }}</span>
          </button>
          <button
            v-if="activeFilters.length > 0"
            class="btn btn-sm btn-link text-muted"
            @click="clearFilters"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>

    <!-- Interactive Timeline (now filterable and scrollable) -->
    <div class="timeline-section card mb-4">
      <div class="card-header d-flex align-items-center justify-content-between py-2">
        <div>
          <h5 class="mb-0">
            <i class="ri-time-line text-primary me-2"></i>Loan Journey Timeline
          </h5>
          <small class="text-muted">Key milestones and events from acquisition to present</small>
        </div>
        <div class="d-flex gap-2">
          <span class="badge bg-light text-dark">{{ filteredEvents.length }} events</span>
          <span class="badge bg-primary-subtle text-primary">{{ activeDays }} days active</span>
        </div>
      </div>
      
      <div class="card-body p-2 timeline-card-body">
        <!-- Visual Timeline (scrollable) -->
        <div class="visual-timeline position-relative">
          <!-- Timeline line -->
          <div class="timeline-line"></div>
          
          <!-- Scrollable timeline events container -->
          <div class="timeline-scroll-container">
            <div class="timeline-events d-flex align-items-end position-relative">
              <div
                v-for="(milestone, index) in filteredMilestones"
                :key="index"
                class="timeline-milestone text-center"
                :class="{ 'active': milestone.active }"
                @click="scrollToEvent(milestone.id)"
              >
                <div class="milestone-dot" :class="`bg-${milestone.color}`">
                  <i :class="milestone.icon"></i>
                </div>
                <div class="milestone-label mt-2">
                  <small class="fw-semibold d-block">{{ milestone.label }}</small>
                  <small class="text-muted">{{ milestone.date }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Story Feed -->
    <div class="story-feed">
      <!-- Loading state -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary mb-3" role="status">
          <span class="visually-hidden">Loading story...</span>
        </div>
        <p class="text-muted">Loading loan narrative...</p>
      </div>

      <!-- Empty state -->
      <div v-else-if="filteredEvents.length === 0" class="text-center py-5">
        <i class="ri-book-open-line fs-1 text-muted mb-3 d-block"></i>
        <h5 class="text-muted">No Events to Display</h5>
        <p class="text-muted small">
          <template v-if="activeFilters.length > 0">
            Try adjusting your filters to see more events
          </template>
          <template v-else>
            The loan story is just beginning...
          </template>
        </p>
      </div>

      <!-- Event feed cards -->
      <div v-else class="events-container">
        <!-- Date group headers -->
        <template v-for="(eventsGroup, date) in groupedEvents" :key="date">
          <div class="date-divider sticky-top bg-body">
            <div class="date-divider-line"></div>
            <span class="date-divider-label badge bg-secondary">
              <i class="ri-calendar-line me-1"></i>{{ formatDateHeader(date) }}
            </span>
            <div class="date-divider-line"></div>
          </div>

          <!-- Events for this date -->
          <div
            v-for="event in eventsGroup"
            :key="event.id"
            :id="`event-${event.id}`"
            class="event-card card mb-2 border-start border-2"
            :class="`border-${getEventColor(event.type)}`"
          >
            <div class="card-body p-1">
              <!-- Event header -->
              <div class="d-flex align-items-start justify-content-between">
                <div class="d-flex align-items-start gap-2 flex-grow-1">
                  <!-- Event icon -->
                  <div
                    class="event-icon rounded-circle d-flex align-items-center justify-content-center"
                    :class="`bg-${getEventColor(event.type)}-subtle text-${getEventColor(event.type)}`"
                  >
                    <i :class="getEventIcon(event.type)" class="fs-5"></i>
                  </div>

                  <!-- Event content -->
                  <div class="flex-grow-1">
                    <!-- Event title with tag badge -->
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <span
                        class="badge"
                        :class="`bg-${getEventColor(event.type)}-subtle text-${getEventColor(event.type)}`"
                      >
                        {{ getEventTypeLabel(event.type) }}
                      </span>
                      <h6 class="mb-0 fw-semibold">{{ event.title }}</h6>
                    </div>

                    <!-- Author info -->
                    <small v-if="event.author" class="text-muted d-block mb-1">
                      <i class="ri-user-line me-1"></i>{{ event.author }}
                    </small>

                    <!-- Event body/description -->
                    <div class="event-body text-muted" v-html="event.body"></div>

                    <!-- Event metadata/tags -->
                    <div v-if="event.tags && event.tags.length > 0" class="mt-1 d-flex flex-wrap gap-1">
                      <span
                        v-for="tag in event.tags"
                        :key="tag"
                        class="badge bg-light text-dark small"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Event actions -->
                <div class="dropdown">
                  <button
                    class="btn btn-sm btn-link text-muted"
                    data-bs-toggle="dropdown"
                  >
                    <i class="ri-more-2-fill"></i>
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="viewEventDetails(event)">
                        <i class="ri-eye-line me-2"></i>View Details
                      </a>
                    </li>
                    <li>
                      <a class="dropdown-item" href="#" @click.prevent="copyEventLink(event)">
                        <i class="ri-link me-2"></i>Copy Link
                      </a>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NarrativeTab.vue
 * 
 * Purpose: Creates a unified narrative view of all loan activities and qualitative data.
 * Design: Timeline header + filterable chronological feed of events from multiple sources.
 * 
 * Features:
 *   - Visual timeline showing key milestones
 *   - Aggregated feed of notes, emails, tasks, and system events
 *   - Filter by event type for focused viewing
 *   - Grouped by date for easy navigation
 *   - Rich event cards with metadata
 * 
 * Documentation reviewed:
 *   - Vue Composition API: https://vuejs.org/guide/essentials/reactivity-fundamentals.html
 *   - Bootstrap Vue Next: https://bootstrap-vue-next.github.io/bootstrap-vue-next/
 */

import { computed, ref, watch, onMounted } from 'vue'
import { useNotesStore } from '@/stores/notes'
import { useAmOutcomesStore } from '@/stores/outcomes'

/**
 * WHAT: Component props passed by the parent LoanTabs component.
 * WHY: Provides asset context for fetching related narrative data.
 * HOW: row and assetHubId used to query APIs for events and notes.
 */
const props = withDefaults(
  defineProps<{
    row?: Record<string, any> | null
    assetHubId?: string | number | null
  }>(),
  {
    row: null,
    assetHubId: null,
  }
)

/**
 * WHAT: Pinia stores for fetching data from various sources.
 * WHY: Reuses existing store infrastructure for notes and outcomes.
 * HOW: Store actions called in loadNarrativeData().
 */
const notesStore = useNotesStore()
const outcomesStore = useAmOutcomesStore()

/**
 * WHAT: Reactive array of all narrative events from various sources.
 * WHY: Central data structure for the story feed.
 * HOW: Populated by loadNarrativeData(), combines notes, tasks, system events.
 */
interface NarrativeEvent {
  id: string
  type: 'note' | 'email' | 'asset_management' | 'milestone' | 'system' | 'communication'
  title: string
  body: string
  timestamp: string
  author?: string
  tags?: string[]
  metadata?: Record<string, any>
}

const allEvents = ref<NarrativeEvent[]>([])

/**
 * WHAT: Loading state flags for async operations.
 * WHY: Controls display of spinners and disabled states.
 * HOW: Toggled in data loading functions.
 */
const loading = ref<boolean>(false)

/**
 * WHAT: Active filter types for event display.
 * WHY: Allows users to focus on specific event categories.
 * HOW: Updated by toggleFilter(), used in filteredEvents computed.
 */
const activeFilters = ref<string[]>([])


/**
 * WHAT: Available event type filters with counts.
 * WHY: Shows users what data is available and allows filtering.
 * HOW: Computed from allEvents data.
 */
const eventFilters = computed(() => [
  {
    type: 'note',
    label: 'Notes',
    icon: 'ri-sticky-note-line',
    count: allEvents.value.filter(e => e.type === 'note').length,
  },
  {
    type: 'asset_management',
    label: 'Asset Management',
    icon: 'ri-file-list-3-line',
    count: allEvents.value.filter(e => e.type === 'asset_management').length,
  },
  {
    type: 'milestone',
    label: 'Milestones',
    icon: 'ri-flag-line',
    count: allEvents.value.filter(e => e.type === 'milestone').length,
  },
  {
    type: 'correspondence',
    label: 'Correspondence',
    icon: 'ri-mail-line',
    count: allEvents.value.filter(e => e.type === 'email' || e.type === 'communication').length,
  },
  {
    type: 'system',
    label: 'System',
    icon: 'ri-settings-3-line',
    count: allEvents.value.filter(e => e.type === 'system').length,
  },
])

/**
 * WHAT: Timeline milestones for visual timeline display.
 * WHY: Highlights key events in the loan lifecycle.
 * HOW: Derived from allEvents or hardcoded placeholders with event type associations.
 */
const milestones = ref([
  { id: 'milestone-1', label: 'Acquisition', date: 'Jan 2024', icon: 'ri-home-4-line', color: 'primary', active: true, eventType: 'milestone' },
  { id: 'milestone-2', label: 'First Contact', date: 'Feb 2024', icon: 'ri-phone-line', color: 'info', active: true, eventType: 'correspondence' },
  { id: 'milestone-3', label: 'Inspection', date: 'Mar 2024', icon: 'ri-search-eye-line', color: 'warning', active: true, eventType: 'asset_management' },
  { id: 'milestone-4', label: 'Negotiations', date: 'Apr 2024', icon: 'ri-chat-3-line', color: 'success', active: false, eventType: 'correspondence' },
  { id: 'milestone-5', label: 'DIL Track', date: 'Active', icon: 'ri-file-list-3-line', color: 'success', active: true, eventType: 'asset_management' },
  { id: 'milestone-6', label: 'Legal Review', date: 'Mar 2024', icon: 'ri-scales-3-line', color: 'warning', active: true, eventType: 'note' },
])

/**
 * WHAT: Computed filtered milestones based on active filters.
 * WHY: Shows only milestones relevant to selected event types.
 * HOW: Filters milestones array by eventType matching activeFilters.
 */
const filteredMilestones = computed(() => {
  if (activeFilters.value.length === 0) return milestones.value
  return milestones.value.filter(m => activeFilters.value.includes(m.eventType))
})

/**
 * WHAT: Computed total event count.
 * WHY: Displays in timeline header.
 * HOW: Returns length of allEvents array.
 */
const totalEvents = computed(() => allEvents.value.length)

/**
 * WHAT: Computed active days since loan acquisition.
 * WHY: Shows loan lifecycle duration in timeline header.
 * HOW: Calculates difference from earliest event to now.
 */
const activeDays = computed(() => {
  if (allEvents.value.length === 0) return 0
  const earliest = new Date(allEvents.value[allEvents.value.length - 1].timestamp)
  const now = new Date()
  return Math.floor((now.getTime() - earliest.getTime()) / (1000 * 60 * 60 * 24))
})

/**
 * WHAT: Computed filtered events based on active filters.
 * WHY: Allows users to narrow down visible events.
 * HOW: Filters allEvents by activeFilters array, with special handling for "correspondence" filter.
 */
const filteredEvents = computed(() => {
  if (activeFilters.value.length === 0) return allEvents.value
  
  return allEvents.value.filter(e => {
    // If "correspondence" filter is active, include both email and communication events
    if (activeFilters.value.includes('correspondence') && (e.type === 'email' || e.type === 'communication')) {
      return true
    }
    // Otherwise, check if the event type matches any active filter
    return activeFilters.value.includes(e.type)
  })
})

/**
 * WHAT: Computed grouped events by date.
 * WHY: Organizes feed with date dividers for easy scanning.
 * HOW: Groups filteredEvents by date string.
 */
const groupedEvents = computed(() => {
  const groups: Record<string, NarrativeEvent[]> = {}
  filteredEvents.value.forEach(event => {
    const dateKey = new Date(event.timestamp).toISOString().split('T')[0]
    if (!groups[dateKey]) groups[dateKey] = []
    groups[dateKey].push(event)
  })
  return groups
})

/**
 * WHAT: Helper to format date headers for feed grouping.
 * WHY: Shows user-friendly date labels (Today, Yesterday, etc.).
 * HOW: Compares date to current date and formats accordingly.
 */
function formatDateHeader(dateString: string): string {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  })
}

/**
 * WHAT: Helper to format relative timestamps for events.
 * WHY: Shows how long ago an event occurred.
 * HOW: Calculates time difference and returns human-readable string.
 */
function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  // Show date only (no time)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

/**
 * WHAT: Helper to get event type label for display.
 * WHY: Converts type codes to user-friendly labels.
 * HOW: Maps event types to display strings.
 */
function getEventTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    note: 'Note',
    email: 'Email',
    asset_management: 'Asset Management',
    milestone: 'Milestone',
    system: 'System Event',
    communication: 'Communication',
  }
  return labels[type] || type
}

/**
 * WHAT: Helper to get color class for event type.
 * WHY: Provides visual differentiation for event categories.
 * HOW: Maps event types to Bootstrap color classes.
 */
function getEventColor(type: string): string {
  const colors: Record<string, string> = {
    note: 'primary',
    email: 'info',
    asset_management: 'success',
    milestone: 'warning',
    system: 'secondary',
    communication: 'purple',
  }
  return colors[type] || 'secondary'
}

/**
 * WHAT: Helper to get icon class for event type.
 * WHY: Visual indicator for event category.
 * HOW: Maps event types to Remix Icon classes.
 */
function getEventIcon(type: string): string {
  const icons: Record<string, string> = {
    note: 'ri-sticky-note-line',
    email: 'ri-mail-line',
    asset_management: 'ri-file-list-3-line',
    milestone: 'ri-flag-line',
    system: 'ri-settings-3-line',
    communication: 'ri-message-3-line',
  }
  return icons[type] || 'ri-information-line'
}

/**
 * WHAT: Function to toggle event type filter.
 * WHY: Allows users to show/hide specific event categories.
 * HOW: Adds or removes type from activeFilters array.
 */
function toggleFilter(type: string): void {
  const index = activeFilters.value.indexOf(type)
  if (index > -1) {
    activeFilters.value.splice(index, 1)
  } else {
    activeFilters.value.push(type)
  }
}

/**
 * WHAT: Function to clear all active filters.
 * WHY: Quick way to show all events again.
 * HOW: Resets activeFilters array to empty.
 */
function clearFilters(): void {
  activeFilters.value = []
}

/**
 * WHAT: Function to scroll to a specific event in the feed.
 * WHY: Allows timeline milestones to jump to related events.
 * HOW: Uses element.scrollIntoView with smooth behavior.
 */
function scrollToEvent(eventId: string): void {
  const element = document.getElementById(`event-${eventId}`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    // Add highlight effect
    element.classList.add('highlight-pulse')
    setTimeout(() => element.classList.remove('highlight-pulse'), 2000)
  }
}

/**
 * WHAT: Function to view detailed event information.
 * WHY: Provides deeper context for complex events.
 * HOW: Could open modal or navigate to detail page (placeholder).
 */
function viewEventDetails(event: NarrativeEvent): void {
  console.log('View details for event:', event)
  // TODO: Implement detail view (modal or navigation)
}

/**
 * WHAT: Function to copy event deep link to clipboard.
 * WHY: Allows sharing specific events with team members.
 * HOW: Constructs URL with event ID and copies to clipboard.
 */
function copyEventLink(event: NarrativeEvent): void {
  const url = `${window.location.origin}${window.location.pathname}#event-${event.id}`
  navigator.clipboard.writeText(url)
  // TODO: Show toast notification
  console.log('Link copied:', url)
}

/**
 * WHAT: Helper to get track label from outcome type.
 * WHY: Converts outcome type codes to user-friendly track names.
 * HOW: Maps outcome types to display labels.
 */
function getTrackLabel(outcomeType: string): string {
  const labels: Record<string, string> = {
    dil: 'Deed-in-Lieu',
    fc: 'Foreclosure',
    reo: 'REO',
    short_sale: 'Short Sale',
    modification: 'Modification',
    note_sale: 'Note Sale',
    performing: 'Performing',
    delinquent: 'Delinquent',
  }
  return labels[outcomeType] || outcomeType
}

/**
 * WHAT: Helper to get task type label for display.
 * WHY: Converts task type codes to readable labels per outcome track.
 * HOW: Maps task types by outcome type.
 */
function getTaskTypeLabel(outcomeType: string, taskType: string): string {
  const labels: Record<string, Record<string, string>> = {
    dil: {
      owner_contacted: 'Borrowers Contacted',
      no_cooperation: 'No Cooperation',
      dil_drafted: 'DIL Drafted',
      dil_successful: 'DIL Executed',
    },
    fc: {
      nod_noi: 'NOD/NOI',
      fc_filing: 'FC Filing',
      mediation: 'Mediation',
      judgement: 'Judgement',
      redemption: 'Redemption',
      sale_scheduled: 'Sale Scheduled',
      sold: 'Sold',
    },
    reo: {
      eviction: 'Eviction',
      trashout: 'Trashout',
      renovation: 'Renovation',
      pre_marketing: 'Pre-Marketing',
      listed: 'Listed',
      under_contract: 'Under Contract',
      sold: 'Sold',
    },
    short_sale: {
      list_price_accepted: 'List Price Accepted',
      listed: 'Listed',
      under_contract: 'Under Contract',
      sold: 'Sold',
    },
    modification: {
      mod_negotiations: 'Negotiations',
      mod_accepted: 'Accepted',
      mod_started: 'Started',
      mod_failed: 'Failed',
    },
    note_sale: {
      potential_note_sale: 'Potential Note Sale',
      out_to_market: 'Out to Market',
      pending_sale: 'Pending Sale',
      sold: 'Sold',
    },
    performing: {
      perf: 'Performing',
      rpl: 'Re-Performing (RPL)',
      note_sold: 'Note Sold',
    },
    delinquent: {
      dq_30: '30 Days Delinquent',
      dq_60: '60 Days Delinquent',
      dq_90: '90 Days Delinquent',
      dq_120_plus: '120+ Days Delinquent',
      loss_mit: 'Loss Mit',
      fc_dil: 'FC/DIL',
    },
  }
  return labels[outcomeType]?.[taskType] || taskType
}

/**
 * WHAT: Core function to load narrative data from all sources.
 * WHY: Aggregates data into unified timeline.
 * HOW: Calls multiple store actions, combines results, sorts chronologically.
 */
async function loadNarrativeData(): Promise<void> {
  const hubId = typeof props.assetHubId === 'number' ? props.assetHubId : Number(props.assetHubId)
  if (!hubId || !Number.isFinite(hubId)) {
    allEvents.value = []
    return
  }

  loading.value = true

  try {
    // Fetch notes
    const notes = await notesStore.listNotes({ assetHubId: hubId })
    
    // Convert notes to events with full content
    const noteEvents: NarrativeEvent[] = notes.map(note => ({
      id: `note-${note.id}`,
      type: 'note',
      title: note.tag ? note.tag.charAt(0).toUpperCase() + note.tag.slice(1) : 'General',
      body: note.body, // Full HTML content from Quill editor
      timestamp: note.created_at,
      author: note.created_by_username || undefined,
      tags: note.tag ? [note.tag] : [],
      metadata: { 
        noteId: note.id,
      },
    }))

    // Fetch AM tasks from all outcome types
    const amEvents: NarrativeEvent[] = []
    const outcomeTypes: Array<'dil' | 'fc' | 'reo' | 'short_sale' | 'modification' | 'note_sale' | 'performing' | 'delinquent'> = ['dil', 'fc', 'reo', 'short_sale', 'modification', 'note_sale', 'performing', 'delinquent']
    
    for (const outcomeType of outcomeTypes) {
      try {
        // Check if outcome exists for this asset
        const outcome = await outcomesStore.fetchOutcome(hubId, outcomeType)
        if (!outcome) continue
        
        // Fetch tasks for this outcome type
        let tasks: any[] = []
        switch (outcomeType) {
          case 'dil':
            tasks = await outcomesStore.listDilTasks(hubId, true)
            break
          case 'fc':
            tasks = await outcomesStore.listFcTasks(hubId, true)
            break
          case 'reo':
            tasks = await outcomesStore.listReoTasks(hubId, true)
            break
          case 'short_sale':
            tasks = await outcomesStore.listShortSaleTasks(hubId, true)
            break
          case 'modification':
            tasks = await outcomesStore.listModificationTasks(hubId, true)
            break
          case 'note_sale':
            tasks = await outcomesStore.listNoteSaleTasks(hubId, true)
            break
          case 'performing':
            tasks = await outcomesStore.listPerformingTasks(hubId, true)
            break
          case 'delinquent':
            tasks = await outcomesStore.listDelinquentTasks(hubId, true)
            break
        }
        
        // Convert tasks to narrative events
        tasks.forEach(task => {
          const trackLabel = getTrackLabel(outcomeType)
          const taskTypeLabel = getTaskTypeLabel(outcomeType, task.task_type)
          
          amEvents.push({
            id: `am-${outcomeType}-${task.id}`,
            type: 'asset_management',
            title: `${trackLabel}: ${taskTypeLabel}`,
            body: task.notes || `<p>${trackLabel} task: ${taskTypeLabel}</p>`,
            timestamp: task.created_at || new Date().toISOString(),
            author: task.created_by_username || 'Asset Management',
            tags: [outcomeType, task.task_type],
            metadata: {
              outcomeType,
              taskType: task.task_type,
              taskId: task.id,
            },
          })
        })
      } catch (error) {
        console.error(`Failed to fetch ${outcomeType} tasks:`, error)
      }
    }
    
    // Combine all events and sort by timestamp
    allEvents.value = [...noteEvents, ...amEvents].sort((a, b) => {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    })

  } catch (error) {
    console.error('Failed to load narrative data:', error)
    allEvents.value = []
  } finally {
    loading.value = false
  }
  
  console.log('Narrative data loaded:', allEvents.value.length, 'events')
}

/**
 * WHAT: Lifecycle hook to load data when component mounts.
 * WHY: Ensures narrative data is fetched on initial render.
 * HOW: Calls loadNarrativeData() on mount.
 */
onMounted(() => {
  loadNarrativeData()
})

/**
 * WHAT: Watch for changes to assetHubId prop.
 * WHY: Reload narrative data when user switches to a different asset.
 * HOW: Watches assetHubId and calls loadNarrativeData() on change.
 */
watch(() => props.assetHubId, (newId, oldId) => {
  if (newId !== oldId) {
    loadNarrativeData()
  }
})
</script>

<style scoped>
/**
 * WHAT: Scoped styles for the Narrative tab.
 * WHY: Creates beautiful, easy-to-follow visual timeline and feed.
 * HOW: Custom CSS for timeline, event cards, and animations.
 */

/* Timeline Card Body - scrollable */
.timeline-card-body {
  max-height: 250px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Custom scrollbar for timeline card */
.timeline-card-body::-webkit-scrollbar {
  width: 6px;
}

.timeline-card-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.timeline-card-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.timeline-card-body::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Timeline Section */
.visual-timeline {
  padding: 2rem 0;
  position: relative;
}

.timeline-line {
  position: absolute;
  top: 2rem;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(to right, #e9ecef 0%, #0d6efd 30%, #0d6efd 70%, #e9ecef 100%);
  border-radius: 2px;
  z-index: 0;
}

/* Scrollable timeline container */
.timeline-scroll-container {
  overflow-x: auto;
  overflow-y: hidden;
  position: relative;
  padding: 0 1rem;
}

/* Custom scrollbar for timeline */
.timeline-scroll-container::-webkit-scrollbar {
  height: 6px;
}

.timeline-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.timeline-scroll-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.timeline-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.timeline-events {
  position: relative;
  z-index: 1;
  min-width: max-content;
  gap: 1rem;
}

.timeline-milestone {
  flex: 1;
  cursor: pointer;
  transition: transform 0.2s ease;
  min-width: 100px;
}

.timeline-milestone:hover {
  transform: translateY(-5px);
}

.milestone-dot {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  border: 4px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-size: 1.5rem;
  color: white;
  transition: all 0.3s ease;
}

.timeline-milestone.active .milestone-dot {
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.4);
  transform: scale(1.1);
}

.timeline-milestone:not(.active) .milestone-dot {
  opacity: 0.6;
  filter: grayscale(50%);
}

.milestone-label {
  font-size: 0.75rem;
  max-width: 100px;
  margin: 0 auto;
}

/* Date Dividers */
.date-divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1rem 0 0.5rem 0;
  padding: 0.25rem 0;
  z-index: 999;
}

.date-divider-line {
  flex: 1;
  height: 2px;
  background: linear-gradient(to right, transparent, #dee2e6, transparent);
}

.date-divider-label {
  white-space: nowrap;
  font-size: 0.85rem;
  padding: 0.35rem 0.75rem;
}

/* Event Cards */
.event-card {
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.event-card:hover {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  transform: translateX(2px);
}

.event-icon {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  font-size: 0.9rem;
}

/* Event body container */
.event-body-container {
  position: relative;
}

/* Event body - show all content without truncation */
.event-body {
  font-size: 0.875rem;
  line-height: 1.4;
  margin-top: 0.25rem;
}

.event-body :deep(p) {
  margin-bottom: 0.125rem;
}

.event-body :deep(p:last-child) {
  margin-bottom: 0;
}

.event-body :deep(ul),
.event-body :deep(ol) {
  margin-bottom: 0.125rem;
  padding-left: 1rem;
}

.event-body :deep(strong),
.event-body :deep(b) {
  font-weight: 600;
  color: #333;
}

.event-body :deep(em),
.event-body :deep(i) {
  font-style: italic;
}

.event-body :deep(a) {
  color: #0d6efd;
  text-decoration: underline;
}

.event-body :deep(a:hover) {
  color: #0a58ca;
}

/* Read more button styling */
.event-body-container .btn-link {
  font-size: 0.85rem;
  color: #0d6efd;
  font-weight: 500;
}

.event-body-container .btn-link:hover {
  color: #0a58ca;
  text-decoration: underline !important;
}

/* Highlight pulse animation for scrolled-to events */
@keyframes highlightPulse {
  0%, 100% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(13, 110, 253, 0.1);
  }
}

.highlight-pulse {
  animation: highlightPulse 1s ease 2;
}

/* Filter buttons */
.filter-section .btn {
  border-radius: 20px;
}

/* Smooth scrolling for the whole tab */
.narrative-tab {
  scroll-behavior: smooth;
}

/* Custom scrollbar for better aesthetics */
.story-feed::-webkit-scrollbar {
  width: 8px;
}

.story-feed::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.story-feed::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.story-feed::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .timeline-milestone {
    min-width: 60px;
  }
  
  .milestone-dot {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .milestone-label {
    font-size: 0.65rem;
    max-width: 70px;
  }
  
  .event-icon {
    width: 36px;
    height: 36px;
  }
}
</style>

