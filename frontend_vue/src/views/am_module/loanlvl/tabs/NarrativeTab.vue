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
          <div class="d-flex align-items-center me-3">
            <span class="small text-muted fw-medium">FILTERS</span>
          </div>
          <button
            v-for="filter in eventFilters"
            :key="filter.type"
            type="button"
            class="btn btn-sm"
            :class="
              activeFilters.length > 0 && activeFilters.includes(filter.type)
                ? 'text-white border-0'
                : 'btn-outline-light text-dark border'
            "
            :style="
              activeFilters.length > 0 && activeFilters.includes(filter.type)
                ? `${getEventBadgeStyle(filter.type)} border-radius: 0.25rem;`
                : 'border-radius: 0.25rem;'
            "
            @click="toggleFilter(filter.type)"
          >
            {{ filter.label }}
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

    <!-- Timeline Component -->
    <div class="card mb-3 shadow-sm">
      <div class="card-header bg-white border-bottom">
        <h5 class="mb-1 d-flex align-items-center">
          <i class="ri-time-line text-primary me-2"></i>Loan Journey Timeline
        </h5>
        <small class="text-muted">Key milestones and events from acquisition to present</small>
      </div>
      <div class="card-body p-2">
        <TimelineView />
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
                        class="badge text-white border-0"
                        :style="getEventBadgeStyle(event.type)"
                      >
                        {{ getEventTypeLabel(event.type) }}
                      </span>
                      <!-- Sub-tag badge for note tags (like "General", "Legal", "Escrow", etc.) -->
                      <span
                        v-if="event.type === 'note'"
                        class="badge text-white border-0 small"
                        :style="getSubTagBadgeStyle(event.tags && event.tags.length > 0 ? event.tags[0] : 'general')"
                      >
                        {{ event.tags && event.tags.length > 0 
                          ? (event.tags[0] === 'borrower_heir' 
                              ? 'Borrower/Heir' 
                              : humanizeLabel(event.tags[0]).replace('Borrower Heir', 'Borrower/Heir'))
                          : 'General' }}
                      </span>
                      <!-- Sub-tag badge for milestone task type -->
                      <span
                        v-if="event.type === 'milestone' && event.tags && event.tags.length > 0"
                        class="badge text-white border-0 small"
                        :style="getTrackBadgeStyle(event.tags[0])"
                      >
                        {{ getTrackBadgeLabel(event.tags[0]) }}
                      </span>
                      <!-- Sub-tag badge for servicer notes -->
                      <span
                        v-if="event.type === 'servicer_notes' && event.tags && event.tags.length > 0"
                        class="badge text-white border-0 small"
                        :style="getSubTagBadgeStyle(event.tags[0])"
                      >
                        {{ humanizeLabel(event.tags[0]) }}
                      </span>
                      <!-- Title for non-note, non-servicer events -->
                      <h6 v-if="event.type !== 'servicer_notes' && event.type !== 'note' && event.type !== 'milestone'" class="mb-0 fw-semibold">{{ event.title }}</h6>
                    </div>

                    <!-- Author info -->
                    <small v-if="event.author && event.type !== 'milestone'" class="text-muted d-block mb-1">
                      <i class="ri-user-line me-1"></i>{{ event.author }}
                    </small>

                    <!-- Event body/description -->
                    <div class="event-body text-muted" v-html="event.body"></div>

                    <!-- Event metadata/tags -->
                    <div
                      v-if="event.type !== 'servicer_notes' && event.type !== 'note' && event.type !== 'milestone' && event.tags && event.tags.length > 0"
                      class="mt-1 d-flex flex-wrap gap-1"
                    >
                      <span
                        v-for="tag in event.tags"
                        :key="tag"
                        class="badge text-white border-0 small"
                        :style="getSubTagBadgeStyle(tag)"
                      >
                        {{ humanizeLabel(tag) }}
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
import http from '@/lib/http'
import { getTagColor, TAG_COLORS } from '@/config/colorPalette'
import { ASSET_PIPELINE_TRACK_COLORS } from '@/config/categoryColors'
import dayjs from 'dayjs'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import TimelineView from '@/components/TimelineView.vue'

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

dayjs.extend(advancedFormat)

type TagColorName = keyof typeof TAG_COLORS

function getTrackTagColor(outcomeType: string): TagColorName {
  const keyMap: Record<string, keyof typeof ASSET_PIPELINE_TRACK_COLORS> = {
    dil: 'DIL',
    fc: 'FC',
    reo: 'REO',
    short_sale: 'Short Sale',
    modification: 'Modification',
    note_sale: 'Note Sale',
    performing: 'Performing',
    delinquent: 'Delinquent',
  }
  const mappedKey = keyMap[outcomeType]
  const tagColor = mappedKey ? ASSET_PIPELINE_TRACK_COLORS[mappedKey] : undefined
  return (tagColor || 'pewter') as TagColorName
}

function getTrackBadgeStyle(outcomeType: string): string {
  return `background-color: ${getTagColor(getTrackTagColor(outcomeType))};`
}

/**
 * WHAT: Reactive array of all narrative events from various sources.
 * WHY: Central data structure for the story feed.
 * HOW: Populated by loadNarrativeData(), combines notes, tasks, system events.
 */
interface NarrativeEvent {
  id: string
  type: 'note' | 'email' | 'asset_management' | 'milestone' | 'system' | 'communication' | 'servicer_notes'
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
    label: 'AM Notes',
    icon: 'ri-sticky-note-line',
    count: allEvents.value.filter(e => e.type === 'note').length,
  },
  {
    type: 'servicer_notes',
    label: 'Servicer Notes',
    icon: 'ri-customer-service-2-line',
    count: allEvents.value.filter(e => e.type === 'servicer_notes').length,
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
 * WHAT: Timeline milestones for PrimeVue Timeline display.
 * WHY: Highlights key events in the loan lifecycle.
 * HOW: Populated dynamically from asset data (acquisition date, track started dates).
 */
const milestones = ref<Array<{ id: string; label: string; dateLabel: string; icon: string; color: string }>>([])

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
    note: 'AM Notes',
    email: 'Email',
    milestone: 'Milestones',
    system: 'System Event',
    communication: 'Communication',
    servicer_notes: 'Servicer Notes',
  }
  if (type === 'asset_management') return labels.milestone
  return labels[type] || type
}

/**
 * WHAT: Helper to get tag color name for event type.
 * WHY: Provides visual differentiation using centralized tag colors.
 * HOW: Maps event types to tag color names from palette.
 */
function getEventTagColor(type: string): TagColorName {
  const tagColors: Record<string, TagColorName> = {
    note: 'eucalyptus',              // #78A083 - Fresh green for notes
    email: 'seafoam',                // #7A9B8E - Blue-green for emails
    milestone: 'warm-yellow',        // #D4A574 - Warm yellow for milestones
    system: 'pewter',                // #8B9196 - Cool gray for system events
    communication: 'heather',       // #9B8FA5 - Soft purple for communication
    servicer_notes: 'info-blue',     // #5A8A95 - Slate teal for servicer notes
    correspondence: 'seafoam',       // #7A9B8E - Blue-green for correspondence
  }
  if (type === 'asset_management') return tagColors.milestone
  return tagColors[type] || 'pewter'
}

/**
 * WHAT: Helper to get inline style for event type badge.
 * WHY: Uses palette tag colors instead of Bootstrap classes.
 * HOW: Returns inline style string with background color from tag palette.
 */
function getEventBadgeStyle(type: string): string {
  const tagColor = getEventTagColor(type)
  return `background-color: ${getTagColor(tagColor)};`
}

/**
 * WHAT: Helper to get sub-tag color for note/event tags.
 * WHY: Uses sub-tag colors from palette for consistent styling.
 * HOW: Maps tag names to sub-tag colors, cycling through available sub-tags.
 */
function getSubTagColor(tagName: string): TagColorName {
  // Sub-tag colors from palette (in order of preference)
  const subTagColors: TagColorName[] = ['mauve', 'heather', 'slate-purple', 'pewter', 'graphite', 'ash']
  
  // Create a simple hash from tag name to consistently assign colors
  const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const index = hash % subTagColors.length
  
  return subTagColors[index]
}

/**
 * WHAT: Helper to get inline style for sub-tag badge.
 * WHY: Uses palette sub-tag colors for consistent styling.
 * HOW: Returns inline style string with background color from sub-tag palette.
 */
function getSubTagBadgeStyle(tagName: string): string {
  const tagColor = getSubTagColor(tagName)
  return `background-color: ${getTagColor(tagColor)};`
}

/**
 * WHAT: Helper to get Bootstrap color class for event type (legacy support).
 * WHY: Still used for some UI elements that need Bootstrap classes.
 * HOW: Maps event types to Bootstrap color classes.
 */
function getEventColor(type: string): string {
  const colors: Record<string, string> = {
    note: 'primary',
    email: 'info',
    milestone: 'warning',
    system: 'secondary',
    communication: 'purple',
    servicer_notes: 'info',
  }
  if (type === 'asset_management') return colors.milestone
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
    milestone: 'ri-flag-line',
    system: 'ri-settings-3-line',
    communication: 'ri-message-3-line',
    servicer_notes: 'ri-customer-service-2-line',
  }
  if (type === 'asset_management') return icons.milestone
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
  if (!eventId) return
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

function humanizeLabel(value: string): string {
  if (!value) return ''

  const acronyms = new Set(['DIL', 'REO', 'FC', 'NOD', 'NOI'])

  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .split(' ')
    .filter(Boolean)
    .map(word => {
      const upper = word.toUpperCase()
      if (acronyms.has(upper)) return upper
      return upper.charAt(0) + upper.slice(1).toLowerCase()
    })
    .join(' ')
}

function formatJourneyDate(value: unknown): string {
  if (!value) return '—'
  const d = dayjs(String(value))
  if (!d.isValid()) return '—'
  return d.format('MMM Do YYYY')
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

function getTrackBadgeLabel(outcomeType: string): string {
  const labels: Record<string, string> = {
    dil: 'DIL',
    fc: 'Foreclosure',
    reo: 'REO',
    short_sale: 'Short Sale',
    modification: 'Modification',
    note_sale: 'Note Sale',
    performing: 'Performing',
    delinquent: 'Delinquent',
  }
  return labels[outcomeType] || (outcomeType ? outcomeType.toUpperCase() : '')
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
      dq_30: '30 DLQ',
      dq_60: '60 DLQ',
      dq_90: '90 DLQ',
      dq_120_plus: '120+ DLQ',
      loss_mit: 'Loss Mit',
      fc_dil: 'FC/DIL',
    },
  }
  return labels[outcomeType]?.[taskType] || humanizeLabel(taskType)
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

  const purchaseDate = props.row?.purchase_date
  milestones.value = [
    {
      id: 'journey-acquisition',
      label: 'Acquisition',
      dateLabel: formatJourneyDate(purchaseDate),
      icon: 'ri-home-4-line',
      color: 'primary',
    },
  ]

  loading.value = true

  try {
    // Fetch notes
    const notes = await notesStore.listNotes({ assetHubId: hubId })
    
    // Convert notes to events with full content
    const noteEvents: NarrativeEvent[] = notes.map(note => ({
      id: `note-${note.id}`,
      type: 'note',
      title: note.tag ? note.tag.charAt(0).toUpperCase() + note.tag.slice(1).replace('_', '/') : 'General',
      body: note.body, // Full HTML content from Quill editor
      timestamp: note.created_at,
      author: note.created_by_username || undefined,
      tags: note.tag ? [note.tag] : ['general'], // Use 'general' as default tag if none assigned
      metadata: { 
        noteId: note.id,
      },
    }))

    // Fetch servicer comments
    let servicerCommentEvents: NarrativeEvent[] = []
    try {
      const assetId = props.row?.id || hubId
      const { data: comments } = await http.get(`/am/assets/${assetId}/servicer_comments/`)
      
      servicerCommentEvents = comments.map((comment: any) => ({
        id: `servicer-comment-${comment.id}`,
        type: 'servicer_notes',
        title: comment.comment, // Just the comment type as title
        body: comment.additional_notes
          ? `<p><strong>${comment.comment}</strong> ${comment.additional_notes}</p>`
          : `<p><strong>${comment.comment}</strong></p>`,
        timestamp: comment.created_at,
        tags: [comment.department], // Department as sub-tag
        metadata: {
          commentId: comment.id,
          commentDate: comment.comment_date,
          department: comment.department,
          investorLoanNumber: comment.investor_loan_number,
        },
      }))
    } catch (error) {
      console.error('Failed to fetch servicer comments:', error)
    }

    // Fetch AM tasks from all outcome types
    const amEvents: NarrativeEvent[] = []
    const outcomeTypes: Array<'dil' | 'fc' | 'reo' | 'short_sale' | 'modification' | 'note_sale' | 'performing' | 'delinquent'> = ['dil', 'fc', 'reo', 'short_sale', 'modification', 'note_sale', 'performing', 'delinquent']
    
    const trackMilestones: Array<{ id: string; label: string; dateLabel: string; icon: string; color: string }> = []

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
            type: 'milestone',
            title: `${trackLabel}: ${taskTypeLabel}`,
            body: task.notes || `<p>${taskTypeLabel}</p>`,
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

        const trackStartCandidate = tasks
          .map(t => t.task_started || t.created_at)
          .filter(Boolean)
          .map((v: any) => String(v))
          .sort((a: string, b: string) => Date.parse(a) - Date.parse(b))[0]

        const firstEventId = tasks.length > 0 ? `am-${outcomeType}-${tasks[0].id}` : ''
        trackMilestones.push({
          id: firstEventId || `journey-track-${outcomeType}`,
          label: `${getTrackLabel(outcomeType)} Track`,
          dateLabel: trackStartCandidate ? formatJourneyDate(trackStartCandidate) : 'Active',
          icon: 'ri-flag-line',
          color: 'warning',
        })
      } catch (error) {
        console.error(`Failed to fetch ${outcomeType} tasks:`, error)
      }
    }

    milestones.value = [
      milestones.value[0],
      ...trackMilestones,
    ]
    
    // Combine all events and sort by timestamp
    allEvents.value = [...noteEvents, ...servicerCommentEvents, ...amEvents].sort((a, b) => {
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
  overflow: visible;
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

