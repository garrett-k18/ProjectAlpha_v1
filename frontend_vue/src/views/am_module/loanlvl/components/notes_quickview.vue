<template>
  <!--
    Notes QuickView component for the Snapshot tab.
    WHAT: Displays a scrollable list of all notes for the specific asset.
    WHY: Gives users quick visibility into note history without leaving the Snapshot tab.
    HOW: Uses the Pinia notes store to fetch and display notes in a compact, read-only format.
  -->
  <div class="card h-100 w-100">
    <!-- Header matches Hyper UI card conventions for consistency -->
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Notes</h4>
      <!-- Badge showing total note count -->
      <span class="badge bg-light text-dark">{{ notes.length }}</span>
    </div>

    <div class="card-body p-0">
      <!-- Guard: show message if no asset hub id is available -->
      <div v-if="!hasHubId" class="text-muted small p-3">
        Select an asset to load notes.
      </div>

      <!-- Loading indicator follows Bootstrap spinner guidance -->
      <div v-else-if="isLoading" class="d-flex align-items-center gap-2 text-muted small p-3">
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Loading notes...
      </div>

      <!-- Display backend or fetch errors -->
      <div v-else-if="loadError" class="alert alert-warning m-3 py-2 px-3 small mb-0">
        {{ loadError }}
      </div>

      <!-- Scrollable notes list -->
      <div v-else class="notes-list-container">
        <!-- Empty state when no notes exist -->
        <div v-if="notes.length === 0" class="text-center text-muted py-4 px-3">
          <i class="ri-sticky-note-line fs-2 d-block mb-2"></i>
          <p class="mb-0">No notes yet</p>
        </div>

        <!-- Notes list -->
        <ul v-else class="list-unstyled mb-0">
          <li
            v-for="note in notes"
            :key="note.id"
            class="note-item border-bottom"
          >
            <!-- Note metadata header -->
            <div class="d-flex justify-content-between align-items-start mb-1">
              <div class="text-muted small">
                <i class="ri-user-line me-1"></i>
                <span class="fw-semibold text-dark">{{ note.created_by_username || 'Unknown' }}</span>
              </div>
              <div class="d-flex align-items-center gap-2">
                <!-- Tag badge if present -->
                <span
                  v-if="note.tag"
                  class="badge"
                  :class="tagBadgeClass(note.tag)"
                >
                  {{ displayTag(note.tag) }}
                </span>
                <!-- Pinned indicator -->
                <i
                  v-if="note.pinned"
                  class="ri-pushpin-fill text-warning"
                  title="Pinned"
                ></i>
              </div>
            </div>

            <!-- Note body content (HTML from Quill editor) -->
            <div class="note-body mb-2" v-html="note.body"></div>

            <!-- Note footer with timestamp and context -->
            <div class="d-flex justify-content-between align-items-center">
              <div class="text-muted small">
                <i class="ri-time-line me-1"></i>
                {{ formatDateTime(note.created_at) }}
              </div>
              <!-- Context badge if note is scoped to an outcome/task -->
              <span
                v-if="note.context_outcome"
                class="badge bg-light text-dark small"
              >
                {{ formatContext(note) }}
              </span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NotesQuickView.vue
 * 
 * Purpose: Read-only, scrollable notes viewer for the Snapshot tab.
 * Design: Uses Pinia notes store for data fetching and caching.
 * Styling: Follows Hyper UI card patterns for visual consistency.
 * 
 * Documentation reviewed:
 * - Pinia store usage: https://pinia.vuejs.org/core-concepts/
 * - Vue Composition API: https://vuejs.org/guide/essentials/reactivity-fundamentals.html
 * - Bootstrap utility classes: https://getbootstrap.com/docs/5.3/utilities/spacing/
 */

import { computed, defineProps, onMounted, ref, watch } from 'vue'
import { useNotesStore, type NoteItem, type NoteTag, type OutcomeKey } from '@/stores/notes'

/**
 * WHAT: Component props passed by the Snapshot tab parent.
 * WHY: Provides the asset row payload plus resolved hub id for API queries.
 * HOW: Both props are optional to keep component reusable in other contexts.
 */
const props = defineProps<{
  row?: Record<string, any> | null
  assetHubId?: string | number | null
}>()

/**
 * WHAT: Shared Pinia notes store for fetching and caching notes data.
 * WHY: Centralizes note CRUD operations and prevents duplicate fetches.
 * HOW: Store docs: https://pinia.vuejs.org/core-concepts/
 */
const notesStore = useNotesStore()

/**
 * WHAT: Reactive array of notes for the current asset.
 * WHY: Drives the template rendering of the scrollable notes list.
 * HOW: Populated by `loadNotes()` function on mount and hub id changes.
 */
const notes = ref<NoteItem[]>([])

/**
 * WHAT: Loading flag toggled while we query the notes API.
 * WHY: Drives the spinner to avoid jarring empty state flicker.
 * HOW: Set inside `loadNotes()` following Vue docs on reactive refs.
 */
const isLoading = ref<boolean>(false)

/**
 * WHAT: Human-readable error message for fetch failures.
 * WHY: Snapshot tab should show a warning instead of breaking the modal.
 * HOW: Updated within `loadNotes()` catch blocks.
 */
const loadError = ref<string | null>(null)

/**
 * WHAT: Computed hub id resolved from props.row or assetHubId prop.
 * WHY: Snapshot rows sometimes provide ids as strings; we normalize to number.
 * HOW: Prefers explicit prop, then row.asset_hub_id, then row.id.
 */
const normalizedHubId = computed<number | null>(() => {
  const explicit = props.assetHubId
  const fromRow = props.row && (props.row as any).asset_hub_id
  const fallbackId = props.row && (props.row as any).id
  const candidate = explicit ?? fromRow ?? fallbackId
  const numeric = candidate != null ? Number(candidate) : NaN
  return Number.isFinite(numeric) ? numeric : null
})

/**
 * WHAT: Boolean flag indicating whether we have a valid hub id to query with.
 * WHY: Controls initial empty state messaging in the template.
 * HOW: True when normalizedHubId returns a concrete number.
 */
const hasHubId = computed<boolean>(() => normalizedHubId.value != null)

/**
 * WHAT: Helper to format ISO timestamp into user-friendly date/time string.
 * WHY: Backend returns ISO strings; we present locale date for better UX.
 * HOW: Uses toLocaleString() for automatic browser locale formatting.
 * @param iso - ISO 8601 timestamp string from backend.
 * @returns Formatted date/time string or original value if parsing fails.
 */
function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

/**
 * WHAT: Helper to convert tag codes to user-friendly display labels.
 * WHY: Backend stores tags as short codes; UI shows readable names.
 * HOW: Maps known tag values to display strings.
 * @param tag - Tag code from NoteItem.
 * @returns Display-friendly tag label.
 */
function displayTag(tag?: NoteTag): string {
  if (!tag) return ''
  const map: Record<string, string> = {
    urgent: 'Urgent',
    legal: 'Legal',
    qc: 'QC',
    ops: 'Operations',
    info: 'Info',
  }
  return map[tag] || tag
}

/**
 * WHAT: Helper to determine Bootstrap badge class based on tag type.
 * WHY: Provides visual color coding for different note categories.
 * HOW: Maps tag codes to Bootstrap badge variant classes.
 * @param tag - Tag code from NoteItem.
 * @returns Bootstrap badge class string.
 */
function tagBadgeClass(tag?: NoteTag): string {
  if (!tag) return 'bg-light text-dark'
  const map: Record<string, string> = {
    urgent: 'bg-danger',
    legal: 'bg-warning',
    qc: 'bg-info',
    ops: 'bg-primary',
    info: 'bg-secondary',
  }
  return map[tag] || 'bg-light text-dark'
}

/**
 * WHAT: Helper to format note context (outcome + task type) into readable string.
 * WHY: Shows which outcome/task track the note belongs to for better context.
 * HOW: Combines outcome and task type fields from note metadata.
 * @param note - NoteItem with context fields.
 * @returns Formatted context string or empty if no context.
 */
function formatContext(note: NoteItem): string {
  if (!note.context_outcome) return ''
  
  // Map outcome codes to display names
  const outcomeMap: Record<OutcomeKey, string> = {
    dil: 'DIL',
    fc: 'FC',
    reo: 'REO',
    short_sale: 'Short Sale',
    modification: 'Modification',
  }
  
  const outcomeName = outcomeMap[note.context_outcome] || note.context_outcome
  
  if (note.context_task_type) {
    return `${outcomeName}: ${note.context_task_type}`
  }
  
  return outcomeName
}

/**
 * WHAT: Core loader that fetches notes for the selected asset hub.
 * WHY: Powers the notes list display in the quickview card.
 * HOW: Calls Pinia store action with hub id, handles errors gracefully.
 */
async function loadNotes(): Promise<void> {
  const hubId = normalizedHubId.value
  
  // Guard: exit early if no valid hub id
  if (!hubId) {
    notes.value = []
    return
  }

  isLoading.value = true
  loadError.value = null

  try {
    // Fetch notes from store (will use cache if available)
    const fetchedNotes = await notesStore.listNotes({ assetHubId: hubId })
    notes.value = fetchedNotes
  } catch (error: any) {
    // Capture error message for display in UI
    loadError.value = error?.response?.data?.detail || error?.message || 'Failed to load notes'
    notes.value = []
  } finally {
    isLoading.value = false
  }
}

/**
 * WHAT: Watcher to reload notes whenever the selected hub id changes.
 * WHY: Snapshot modal can switch assets without remounting the component.
 * HOW: Vue watch API per docs (https://vuejs.org/api/reactivity-core.html#watch).
 */
watch(normalizedHubId, () => {
  loadNotes()
})

/**
 * WHAT: Initial load when the component mounts.
 * WHY: Ensures data fetch runs on first render.
 * HOW: Vue lifecycle hook per docs (https://vuejs.org/api/composition-api-lifecycle.html#onmounted).
 */
onMounted(() => {
  loadNotes()
})
</script>

<style scoped>
/**
 * WHAT: Scoped styles for the notes quickview card.
 * WHY: Ensures scrollable list with consistent spacing and typography.
 * HOW: Uses CSS for overflow control and visual polish.
 */

/* Scrollable container for notes list - fixed height with overflow */
.notes-list-container {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Individual note item styling */
.note-item {
  padding: 0.75rem 1rem;
  transition: background-color 0.15s ease;
}

/* Hover effect for better interactivity feedback */
.note-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Last note item doesn't need bottom border */
.note-item:last-child {
  border-bottom: none !important;
}

/* Note body content styling (handles HTML from Quill) */
.note-body {
  font-size: 0.875rem;
  line-height: 1.5;
  color: #333;
}

/* Ensure paragraphs in note body have proper spacing */
.note-body :deep(p) {
  margin-bottom: 0.5rem;
}

/* Remove bottom margin from last paragraph */
.note-body :deep(p:last-child) {
  margin-bottom: 0;
}

/* Headings in note body should be smaller */
.note-body :deep(h1),
.note-body :deep(h2) {
  margin: 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
}

/* Lists in note body */
.note-body :deep(ul),
.note-body :deep(ol) {
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
}

/* Links in note body */
.note-body :deep(a) {
  color: #0d6efd;
  text-decoration: underline;
}

/* Images, videos, iframes should be responsive */
.note-body :deep(img),
.note-body :deep(video),
.note-body :deep(iframe) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0.5rem 0;
}

/* Custom scrollbar styling for webkit browsers */
.notes-list-container::-webkit-scrollbar {
  width: 8px;
}

.notes-list-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.notes-list-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.notes-list-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>

