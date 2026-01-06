<template>
  <!--
    Notes Quick View component for the Snapshot tab.
    WHAT: Displays an AI-powered summary of all notes for the specific asset, plus a quick note composer.
    WHY: Gives users intelligent insights from note history and allows quick note creation without leaving Snapshot.
    HOW: Uses Pinia notes store to fetch notes, analyzes them, and presents key insights and recent highlights.
  -->
  <div class="card h-100 w-100">
    <!-- Header matches Hyper UI card conventions for consistency -->
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Notes Quick View</h4>
      <!-- Add New Note button triggers modal -->
      <button
        class="btn btn-sm btn-primary"
        @click="showNoteModal = true"
        :disabled="!hasHubId"
      >
        <i class="ri-add-line me-1"></i>Add New Note
      </button>
    </div>

    <div class="card-body p-0">
      <!-- Guard: show message if no asset hub id is available -->
      <div v-if="!hasHubId" class="text-muted small p-3">
        Select an asset to load notes.
      </div>

      <!-- Loading indicator follows Bootstrap spinner guidance -->
      <div v-else-if="isLoading && notes.length === 0" class="d-flex align-items-center gap-2 text-muted small p-3">
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Loading notes...
      </div>

      <!-- Display backend or fetch errors -->
      <div v-else-if="loadError && notes.length === 0" class="alert alert-warning m-3 py-2 px-3 small mb-0">
        {{ loadError }}
      </div>

      <!-- Main content area with AI summary at the top -->
      <div v-else>
        <!-- AI Summary Section at the top of card -->
        <div class="notes-summary-container p-3">
          <!-- Empty state when no notes exist -->
          <div v-if="notes.length === 0" class="text-center text-muted py-4">
            <i class="ri-file-list-3-line fs-2 d-block mb-2 opacity-50"></i>
            <p class="mb-0">No notes to summarize yet</p>
            <small class="text-muted">Add your first note above to get started</small>
          </div>

          <!-- AI Summary Display when notes exist -->
          <div v-else class="ai-summary-section">
            <!-- Loading state for AI summary -->
            <div v-if="isLoadingSummary" class="d-flex align-items-center gap-2 text-muted small">
              <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
              {{ summaryError ? 'Loading summary...' : 'Generating AI summary...' }}
            </div>

            <!-- Error state for summary -->
            <div v-else-if="summaryError" class="alert alert-warning py-2 mb-0 small">
              <small>{{ summaryError }}</small>
            </div>

            <!-- AI Summary Content - Clean and concise -->
            <div v-else-if="aiSummary" class="summary-content">
              <!-- Executive Summary -->
              <div v-if="aiSummary.summary_text" class="mb-3">
                <h6 class="text-muted small fw-semibold mb-2">
                  <i class="ri-file-text-line me-1"></i>Summary
                </h6>
                <p class="mb-0">{{ aiSummary.summary_text }}</p>
              </div>

              <!-- Key Insights Section -->
              <div v-if="aiSummary.bullets && aiSummary.bullets.length > 0" class="mb-3">
                <h6 class="text-muted small fw-semibold mb-2">
                  <i class="ri-lightbulb-line me-1"></i>Key Insights
                </h6>
                <ul class="summary-list mb-0">
                  <li v-for="(bullet, idx) in aiSummary.bullets" :key="idx" class="mb-2">
                    <span v-html="formatBullet(bullet)"></span>
                  </li>
                </ul>
              </div>

              <!-- Fallback: Show metadata if AI summary is empty -->
              <div v-else class="mb-3">
                <h6 class="text-muted small fw-semibold mb-2">
                  <i class="ri-lightbulb-line me-1"></i>Key Insights
                </h6>
                <ul class="summary-list mb-0">
                  <li class="mb-2">
                    <span class="fw-semibold">Recent Activity:</span> Most recent note added {{ formatRelativeTime(notes[0]?.created_at) }}
                    <template v-if="notes[0]?.created_by_username">
                      by {{ notes[0].created_by_username }}
                    </template>
                  </li>
                  <li class="mb-2">
                    <span class="fw-semibold">Note Distribution:</span> 
                    {{ getUrgentCount() }} urgent, {{ getLegalCount() }} legal-related, {{ getGeneralCount() }} general notes
                  </li>
                </ul>
              </div>
            </div>

            <!-- Fallback: Show basic metadata if no AI summary available -->
            <div v-else class="summary-content">
              <div class="mb-3">
                <h6 class="text-muted small fw-semibold mb-2">
                  <i class="ri-lightbulb-line me-1"></i>Key Insights
                </h6>
                <ul class="summary-list mb-0">
                  <li class="mb-2">
                    <span class="fw-semibold">Recent Activity:</span> Most recent note added {{ formatRelativeTime(notes[0]?.created_at) }}
                    <template v-if="notes[0]?.created_by_username">
                      by {{ notes[0].created_by_username }}
                    </template>
                  </li>
                  <li class="mb-2">
                    <span class="fw-semibold">Note Distribution:</span> 
                    {{ getUrgentCount() }} urgent, {{ getLegalCount() }} legal-related, {{ getGeneralCount() }} general notes
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add New Note Modal -->
    <b-modal
      v-model="showNoteModal"
      title="Add New Note"
      size="lg"
      centered
      hide-footer
    >
      <!-- Note composer in modal -->
      <div class="mb-3">
        <label class="form-label small text-muted">Note Content</label>
        <QuillEditor
          theme="bubble"
          content-type="html"
          v-model:content="editorHtml"
          :toolbar="toolbarBubble"
          placeholder="Type your note here..."
          style="min-height: 150px; background: #FDFBF7; border: 1px solid #dee2e6; border-radius: 4px; padding: 0.75rem;"
        />
      </div>

      <!-- Modal footer buttons -->
      <div class="d-flex justify-content-end gap-2 mt-3 pt-3 border-top">
        <button
          class="btn btn-sm btn-outline-secondary"
          @click="cancelNote"
          :disabled="saving"
        >
          Cancel
        </button>
        <button
          class="btn btn-sm btn-primary"
          :disabled="saving || !canSubmit"
          @click="submitNote"
        >
          <span v-if="!saving">
            <i class="ri-save-line me-1"></i>Save Note
          </span>
          <span v-else>
            <span class="spinner-border spinner-border-sm me-1" role="status"></span>
            Saving...
          </span>
        </button>
      </div>
    </b-modal>
  </div>
</template>

<script setup lang="ts">
/**
 * NotesQuickView.vue
 * 
 * Purpose: AI-powered notes summary and quick composer for the Snapshot tab.
 * Design: Uses Pinia notes store for data fetching, analyzes notes to generate insights.
 * Features: 
 *   - Quick note composer with Quill rich text editor
 *   - AI summary showing key insights, note distribution, and active topics
 *   - Recent highlights with preview of latest notes
 *   - Note count badge and relative time formatting
 * Styling: Follows Hyper UI card patterns for visual consistency.
 * 
 * Documentation reviewed:
 * - Pinia store usage: https://pinia.vuejs.org/core-concepts/
 * - Vue Composition API: https://vuejs.org/guide/essentials/reactivity-fundamentals.html
 * - Quill Editor: https://vueup.github.io/vue-quill/
 * - Bootstrap utility classes: https://getbootstrap.com/docs/5.3/utilities/spacing/
 */

import { computed, defineProps, onMounted, ref, watch } from 'vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.bubble.css'
import { BModal } from 'bootstrap-vue-next'
import { useNotesStore, type NoteItem, type NoteTag, type OutcomeKey } from '@/stores/notes'
import http from '@/lib/http'

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
 * WHAT: AI-generated summary data from backend.
 * WHY: Stores persisted summary to avoid regenerating on every load.
 * HOW: Fetched from /am/notes/summary/ endpoint.
 */
const aiSummary = ref<{
  summary_text: string
  bullets: string[]
  note_count: number
} | null>(null)

/**
 * WHAT: Loading flag for AI summary fetch.
 * WHY: Shows loading state while fetching summary.
 * HOW: Toggled in loadSummary() function.
 */
const isLoadingSummary = ref<boolean>(false)

/**
 * WHAT: Error message for summary fetch failures.
 * WHY: Allows graceful error handling in UI.
 * HOW: Set in loadSummary() catch block.
 */
const summaryError = ref<string | null>(null)

/**
 * WHAT: Reactive state for the Quill editor content.
 * WHY: Stores the HTML content being composed by the user.
 * HOW: Bound to QuillEditor v-model in template.
 */
const editorHtml = ref<string>('')

/**
 * WHAT: Loading flag for note creation operation.
 * WHY: Disables save button and shows spinner during API call.
 * HOW: Toggled in submitNote() function.
 */
const saving = ref<boolean>(false)

/**
 * WHAT: Boolean flag to control the visibility of the Add New Note modal.
 * WHY: Shows/hides the note composer modal when user clicks "Add New Note" button.
 * HOW: Toggled by button click in header and by modal actions (cancel/save).
 */
const showNoteModal = ref<boolean>(false)

/**
 * WHAT: Quill bubble toolbar configuration for inline editing.
 * WHY: Provides essential formatting tools without overwhelming the compact UI.
 * HOW: Array of toolbar items per Quill documentation.
 */
const toolbarBubble = [
  ['bold', 'italic', 'underline'],
  [{ list: 'ordered' }, { list: 'bullet' }],
  ['link'],
]

/**
 * WHAT: Computed flag indicating whether the note can be submitted.
 * WHY: Prevents saving empty notes (HTML tags only).
 * HOW: Strips HTML tags and checks for actual text content.
 */
const canSubmit = computed(() => {
  if (!editorHtml.value) return false
  const text = editorHtml.value.replace(/<[^>]*>/g, '').trim()
  return text.length > 0
})

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
 * WHAT: Helper to format timestamp into relative time (e.g., "2 hours ago").
 * WHY: Provides quick understanding of note recency in summary view.
 * HOW: Calculates time difference and returns human-readable string.
 * @param iso - ISO 8601 timestamp string from backend.
 * @returns Relative time string (e.g., "3 days ago", "just now").
 */
function formatRelativeTime(iso?: string): string {
  if (!iso) return 'recently'
  
  try {
    const date = new Date(iso)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins === 1 ? '' : 's'} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) === 1 ? '' : 's'} ago`
    return `${Math.floor(diffDays / 30)} month${Math.floor(diffDays / 30) === 1 ? '' : 's'} ago`
  } catch {
    return 'recently'
  }
}

/**
 * WHAT: Helper to count urgent-tagged notes.
 * WHY: Provides insight into critical items in the summary.
 * HOW: Filters notes array by tag value.
 * @returns Count of urgent notes.
 */
function getUrgentCount(): number {
  return notes.value.filter(n => n.tag === 'urgent').length
}

/**
 * WHAT: Helper to count legal-tagged notes.
 * WHY: Provides insight into legal-related items in the summary.
 * HOW: Filters notes array by tag value.
 * @returns Count of legal notes.
 */
function getLegalCount(): number {
  return notes.value.filter(n => n.tag === 'legal').length
}

/**
 * WHAT: Helper to count general (non-urgent, non-legal) notes.
 * WHY: Provides insight into routine notes in the summary.
 * HOW: Filters notes array excluding urgent and legal tags.
 * @returns Count of general notes.
 */
function getGeneralCount(): number {
  return notes.value.filter(n => n.tag !== 'urgent' && n.tag !== 'legal').length
}

/**
 * WHAT: Helper to extract unique active contexts (outcomes) from notes.
 * WHY: Shows which AM tracks are referenced in notes for the summary.
 * HOW: Returns empty array since context fields were removed from simplified note model.
 * @returns Empty array (context tracking removed from notes).
 */
function getActiveContexts(): string[] {
  return []
}

/**
 * WHAT: Helper to get recent note highlights for summary display.
 * WHY: Shows preview of most recent notes in the AI summary section.
 * HOW: Takes top 3 most recent notes and formats them for display.
 * @returns Array of highlight objects with preview data.
 */
function getRecentHighlights(): Array<{ id: number; author: string; time: string; timestamp: string; preview: string }> {
  return notes.value.slice(0, 3).map(note => {
    // Strip HTML tags and truncate for preview
    const text = (note.body || '').replace(/<[^>]*>/g, '').trim()
    const preview = text.length > 100 ? text.substring(0, 100) + '...' : text
    
    // Format actual timestamp (date only)
    const timestamp = note.created_at ? new Date(note.created_at).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    }) : ''
    
    return {
      id: note.id,
      author: note.created_by_username || '',
      time: formatRelativeTime(note.created_at),
      timestamp,
      preview: preview || 'No content',
    }
  })
}

/**
 * WHAT: Formats bullet point text by making the label bold.
 * WHY: Removes markdown formatting and makes labels stand out visually.
 * HOW: Strips ** markers, finds text before colon, and wraps label in <strong> tags.
 * @param bullet - The bullet point text to format
 * @returns HTML string with bold label
 */
function formatBullet(bullet: string): string {
  if (!bullet) return ''
  
  // WHAT: Strip markdown bold markers (**text**)
  // WHY: Remove unwanted markdown formatting
  // HOW: Replace ** with empty string
  let cleaned = bullet.replace(/\*\*/g, '')
  
  // WHAT: Find label (text before colon) and description (text after colon)
  // WHY: Want to make label bold, keep description normal
  // HOW: Split on colon if present
  const colonIndex = cleaned.indexOf(':')
  
  if (colonIndex > 0 && colonIndex < cleaned.length - 1) {
    // WHAT: Split into label and description
    // WHY: Need to format them separately
    // HOW: Split at colon position
    const label = cleaned.substring(0, colonIndex).trim()
    const description = cleaned.substring(colonIndex + 1).trim()
    
    // WHAT: Return formatted HTML with bold label
    // WHY: Make label stand out visually
    // HOW: Wrap label in <strong> tags
    return `<strong>${escapeHtml(label)}:</strong> ${escapeHtml(description)}`
  }
  
  // WHAT: No colon found, return text as-is (but escape HTML)
  // WHY: Some bullets might not have label format
  // HOW: Just escape and return
  return escapeHtml(cleaned)
}

/**
 * WHAT: Escapes HTML special characters to prevent XSS.
 * WHY: User-generated content needs to be sanitized.
 * HOW: Replace HTML special characters with entities.
 * @param text - Text to escape
 * @returns Escaped HTML string
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
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
    
    // WHAT: Load AI summary after notes are loaded
    // WHY: Summary depends on notes existing
    // HOW: Call loadSummary function
    await loadSummary()
  } catch (error: any) {
    // Capture error message for display in UI
    loadError.value = error?.response?.data?.detail || error?.message || 'Failed to load notes'
    notes.value = []
  } finally {
    isLoading.value = false
  }
}

/**
 * WHAT: Fetches AI-generated summary for the current asset hub.
 * WHY: Provides intelligent summary without regenerating on every load.
 * HOW: Calls /am/notes/summary/ endpoint which returns persisted summary.
 */
async function loadSummary(): Promise<void> {
  const hubId = normalizedHubId.value
  
  // WHAT: Guard against missing hub id
  // WHY: Can't fetch summary without asset hub
  // HOW: Exit early if no hub id
  if (!hubId) {
    aiSummary.value = null
    return
  }

  // WHAT: Don't fetch summary if no notes exist
  // WHY: Summary requires notes to be meaningful
  // HOW: Check notes array length
  if (notes.value.length === 0) {
    aiSummary.value = null
    return
  }

  isLoadingSummary.value = true
  summaryError.value = null

  try {
    // WHAT: Fetch summary from backend API
    // WHY: Backend handles generation/caching logic
    // HOW: GET request to summary endpoint with asset_hub_id param
    const response = await http.get<{
      summary_text: string
      bullets: string[]
      note_count: number
      error?: boolean
      detail?: string
    }>('/am/notes/summary/', {
      params: { asset_hub_id: hubId }
    })
    
    // WHAT: Check if response indicates an error
    // WHY: Backend may return 200 with error flag
    // HOW: Check for error flag or empty summary
    if (response.data.error || (response.data.detail && !response.data.summary_text && !response.data.bullets?.length)) {
      // WHAT: Handle backend error response
      // WHY: Backend returned error but with 200 status
      // HOW: Set error message
      summaryError.value = response.data.detail || 'Failed to generate summary'
      console.error('Summary generation error:', response.data.detail)
    } else if (response.data.summary_text || (response.data.bullets && response.data.bullets.length > 0)) {
      // WHAT: Store summary data if valid
      // WHY: Display in template
      // HOW: Assign response data to aiSummary ref
      aiSummary.value = {
        summary_text: response.data.summary_text || '',
        bullets: response.data.bullets || [],
        note_count: response.data.note_count || 0,
      }
      console.log('Summary loaded successfully:', aiSummary.value)
    } else {
      // WHAT: Handle empty summary response
      // WHY: Summary might be empty but valid
      // HOW: Set summary to null to show fallback
      console.warn('Empty summary response received')
      aiSummary.value = null
    }
  } catch (error: any) {
    // WHAT: Handle errors gracefully
    // WHY: Don't break UI if summary fails
    // HOW: Store error message, keep existing summary if available
    const errorMsg = error?.response?.data?.detail || error?.message || 'Failed to load summary'
    summaryError.value = errorMsg
    console.error('Error loading summary:', error)
    // WHAT: Don't clear existing summary on error
    // WHY: Better UX to show stale summary than nothing
    // HOW: Only set error, don't clear aiSummary
  } finally {
    isLoadingSummary.value = false
  }
}

/**
 * WHAT: Function to submit a new note to the backend.
 * WHY: Allows users to add notes directly from the quickview modal.
 * HOW: Calls Pinia store action to create note, then closes modal and refreshes list.
 */
async function submitNote(): Promise<void> {
  const hubId = normalizedHubId.value
  
  // Guard: ensure we have valid hub id and content
  if (!hubId || !canSubmit.value) return

  saving.value = true

  try {
    // Create note via store action
    await notesStore.createNote(hubId, {
      body: editorHtml.value,
    })
    
    // Clear editor and close modal on success
    editorHtml.value = ''
    showNoteModal.value = false
    
    // WHAT: Reload notes to show the new entry
    // WHY: Update UI with latest notes
    // HOW: Call loadNotes which also triggers summary regeneration via backend signal
    await loadNotes()
    
    // WHAT: Reload summary after note creation
    // WHY: Summary should update when notes change (backend signal handles regeneration, but we refresh display)
    // HOW: Call loadSummary to fetch updated summary
    await loadSummary()
  } catch (error: any) {
    // Show error in console for debugging
    console.error('Failed to create note:', error)
    // Optionally show error to user
    loadError.value = error?.response?.data?.detail || error?.message || 'Failed to create note'
  } finally {
    saving.value = false
  }
}

/**
 * WHAT: Function to cancel note creation and close the modal.
 * WHY: Allows user to dismiss the note composer without saving.
 * HOW: Clears editor content and closes modal.
 */
function cancelNote(): void {
  editorHtml.value = ''
  showNoteModal.value = false
}

/**
 * WHAT: Function to clear the editor content.
 * WHY: Allows user to reset the note composer without submitting.
 * HOW: Sets editorHtml to empty string.
 */
function clearEditor(): void {
  editorHtml.value = ''
}

/**
 * WHAT: Watcher to reload notes whenever the selected hub id changes.
 * WHY: Snapshot modal can switch assets without remounting the component.
 * HOW: Vue watch API per docs (https://vuejs.org/api/reactivity-core.html#watch).
 */
watch(normalizedHubId, () => {
  loadNotes()
  // Also clear editor when switching assets
  clearEditor()
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
 * WHY: Ensures scrollable summary with consistent spacing and typography.
 * HOW: Uses CSS for overflow control and visual polish.
 */

/* Summary container styling - now takes full card height */
.notes-summary-container {
  max-height: 450px;
  overflow-y: auto;
  overflow-x: hidden;
  font-size: 0.875rem;
}

/* AI summary section styling */
.ai-summary-section {
  line-height: 1.6;
}

/* Summary list styling */
.summary-list {
  list-style: none;
  padding-left: 0;
}

.summary-list li {
  position: relative;
  padding-left: 1.25rem;
}

.summary-list li::before {
  content: '•';
  position: absolute;
  left: 0.25rem;
  color: #0d6efd;
  font-weight: bold;
}

/* Highlight item styling */
.highlight-item {
  transition: all 0.2s ease;
}

.highlight-item:hover {
  background-color: #e7f3ff !important;
  transform: translateX(2px);
}

/* Custom scrollbar styling for webkit browsers */
.notes-summary-container::-webkit-scrollbar {
  width: 8px;
}

.notes-summary-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.notes-summary-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.notes-summary-container::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}
</style>

