<template>
  <!--
    WHAT: Master Notes Section - Unified notes panel for all outcomes
    WHY: Consolidate notes from all outcome types into single view instead of scattered sections
    WHERE: AM Tasking page, second column next to track outcomes
    HOW: Shows all notes for asset with outcome tag badges, allows manual tagging, filterable
    
    Documentation reviewed:
    - Pinia: https://pinia.vuejs.org/core-concepts/
    - DRF filtering: https://www.django-rest-framework.org/api-guide/filtering/
  -->
  <div class="card h-100">
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Notes</h4>
      <!-- WHAT: Compact filter dropdown for outcome type -->
      <!-- WHY: Less visual clutter than button group -->
      <!-- HOW: Select element with all outcome options -->
      <select 
        v-model="filterOutcome" 
        class="form-select form-select-sm" 
        style="max-width: 150px;"
      >
        <option :value="null">All Notes</option>
        <option 
          v-for="outcome in availableOutcomes" 
          :key="outcome.key"
          :value="outcome.key"
        >
          {{ outcome.label }}
        </option>
      </select>
    </div>
    
    <div class="card-body p-3">
      <!-- Composer: Add new note -->
      <!-- WHAT: Simple note composer without tag selector -->
      <!-- WHY: Keep creation simple, users can tag via edit after creation -->
      <!-- HOW: Just textarea and submit button, notes default to untagged -->
      <form class="mb-3 d-flex gap-2" @submit.prevent="onAddNote">
        <textarea
          v-model="draft"
          class="form-control form-control-sm"
          rows="2"
          placeholder="Add a note..."
          aria-label="Add a note"
        ></textarea>
        <button 
          type="submit" 
          class="btn btn-sm btn-primary align-self-start" 
          :disabled="submitting || !draft.trim()"
        >
          <span v-if="submitting">
            <i class="fas fa-spinner fa-spin me-1"></i>Adding...
          </span>
          <span v-else>
            <i class="fas fa-plus me-1"></i>Add
          </span>
        </button>
      </form>

      <!-- Notes list (scrollable) -->
      <div class="notes-list" style="max-height: 600px; overflow-y: auto;">
        <!-- Loading state -->
        <div v-if="loading" class="text-center text-muted py-3">
          <i class="fas fa-spinner fa-spin me-2"></i>
          Loading notes...
        </div>
        
        <!-- Empty state -->
        <div v-else-if="filteredNotes.length === 0" class="text-muted small text-center py-3">
          {{ filterOutcome ? `No ${getOutcomeLabel(filterOutcome)} notes yet.` : 'No notes yet.' }}
        </div>
        
        <!-- Notes feed -->
        <div v-else class="d-flex flex-column gap-2">
          <div
            v-for="note in filteredNotes"
            :key="note.id"
            class="note-card px-3 py-2 rounded border position-relative"
            :class="getNoteCardClass(note)"
          >
            <!-- Edit mode -->
            <!-- WHAT: Simple inline note editor -->
            <!-- WHY: Quick edits without tag management (AI will auto-tag later) -->
            <!-- HOW: Textarea with save/cancel buttons -->
            <div v-if="editingNoteId === note.id" class="d-flex gap-2">
              <textarea
                v-model="editDraft"
                class="form-control form-control-sm"
                rows="2"
                @keyup.enter.ctrl="saveEdit(note.id)"
                @keyup.esc="cancelEdit"
                ref="editInput"
              ></textarea>
              <div class="d-flex flex-column gap-1">
                <button class="btn btn-sm btn-success" @click="saveEdit(note.id)" :disabled="!editDraft.trim()">
                  <i class="fas fa-check"></i>
                </button>
                <button class="btn btn-sm btn-secondary" @click="cancelEdit">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <!-- View mode -->
            <div v-else>
              <!-- Note header: timestamp, tag, actions -->
              <div class="d-flex align-items-center justify-content-between mb-1">
                <div class="d-flex align-items-center gap-2">
                  <span class="small text-muted">{{ localTime(note.created_at) }}</span>
                  <UiBadge 
                    v-if="note.context_outcome" 
                    :tone="getBadgeTone(note.context_outcome)" 
                    size="xs"
                  >
                    {{ getOutcomeLabel(note.context_outcome) }}
                  </UiBadge>
                </div>
                
                <!-- Action buttons (show on hover) -->
                <div class="note-actions d-flex gap-1">
                  <button 
                    class="btn btn-sm btn-outline-primary px-1 py-0" 
                    @click="startEdit(note)" 
                    title="Edit note"
                    style="font-size: 0.7rem;"
                  >
                    <i class="mdi mdi-pencil"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger px-1 py-0" 
                    @click="deleteNote(note.id)" 
                    title="Delete note"
                    style="font-size: 0.7rem;"
                  >
                    <i class="mdi mdi-delete"></i>
                  </button>
                </div>
              </div>
              
              <!-- Note body -->
              <div class="small" style="white-space: pre-wrap;">{{ note.body }}</div>
              
              <!-- Note footer: author -->
              <div class="small text-muted mt-1" style="font-size: 0.7rem;">
                <i class="mdi mdi-account-circle me-1"></i>{{ note.created_by_username || 'User' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirm Delete Modal -->
  <template v-if="showDeleteConfirm">
    <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
    <div class="modal fade show" tabindex="-1" role="dialog" aria-modal="true"
         style="display: block; position: fixed; inset: 0; z-index: 1055;">
      <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header bg-danger-subtle">
            <h5 class="modal-title d-flex align-items-center">
              <i class="fas fa-triangle-exclamation text-danger me-2"></i>
              Confirm Deletion
            </h5>
            <button type="button" class="btn-close" aria-label="Close" @click="cancelDelete"></button>
          </div>
          <div class="modal-body">
            <p class="mb-0">Are you sure you want to delete this note? This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-light" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useNotesStore, type NoteItem, type OutcomeKey } from '@/stores/notes'
import UiBadge from '@/components/ui/UiBadge.vue'
import type { BadgeToneKey } from '@/config/badgeTokens'

// WHAT: Component props for asset hub identification
// WHY: Load all notes for this specific asset
// HOW: hubId used to fetch notes from API
const props = defineProps<{
  hubId: number
}>()

// WHAT: Pinia store for notes management
// WHY: Centralized state management for notes data
// HOW: Access via useNotesStore composable
const store = useNotesStore()

// WHAT: Filter state for showing specific outcome notes
// WHY: Allow users to focus on notes for specific track (FC, REO, DIL, etc.)
// HOW: null shows all, otherwise filters to specific outcome key
const filterOutcome = ref<OutcomeKey | null>(null)

// WHAT: Loading state from store
// WHY: Show loading indicator while fetching notes
// HOW: Computed from store's loadingByHub map
const loading = computed(() => store.loadingByHub[props.hubId] ?? false)

// WHAT: All notes for this asset hub
// WHY: Master list to filter and display
// HOW: Get from store, already loaded for this hub
const allNotes = computed<NoteItem[]>(() => store.getNotesForHub(props.hubId))

// WHAT: Filtered notes based on selected outcome filter
// WHY: Show only relevant notes when filter is active
// HOW: If filterOutcome is null, show all; otherwise filter by context_outcome
const filteredNotes = computed<NoteItem[]>(() => {
  if (filterOutcome.value === null) {
    return allNotes.value
  }
  return allNotes.value.filter(n => n.context_outcome === filterOutcome.value)
})

// WHAT: Available outcome types for tagging/filtering
// WHY: Provide consistent list of outcomes for UI
// HOW: Static array with label, key, and badge tone
const availableOutcomes = [
  { key: 'fc' as OutcomeKey, label: 'FC', tone: 'danger' },
  { key: 'reo' as OutcomeKey, label: 'REO', tone: 'success' },
  { key: 'dil' as OutcomeKey, label: 'DIL', tone: 'info' },
  { key: 'short_sale' as OutcomeKey, label: 'Short Sale', tone: 'warning' },
  { key: 'modification' as OutcomeKey, label: 'Mod', tone: 'secondary' },
  { key: 'note_sale' as OutcomeKey, label: 'Note Sale', tone: 'primary' },
]

// WHAT: Get human-readable label for outcome key
// WHY: Display friendly names instead of keys (fc → FC, short_sale → Short Sale)
// HOW: Find in availableOutcomes array
function getOutcomeLabel(outcomeKey: OutcomeKey): string {
  const found = availableOutcomes.find(o => o.key === outcomeKey)
  return found ? found.label : outcomeKey
}

// WHAT: Get badge tone/color for outcome key
// WHY: Visual consistency with outcome cards
// HOW: Map outcome key to badge color class
function getBadgeTone(outcomeKey: OutcomeKey): BadgeToneKey {
  const found = availableOutcomes.find(o => o.key === outcomeKey)
  return (found ? found.tone : 'secondary') as BadgeToneKey
}

// WHAT: Get card background class based on outcome tag
// WHY: Visually distinguish notes by outcome type
// HOW: Light background colors matching badge tones
function getNoteCardClass(note: NoteItem): string {
  if (!note.context_outcome) return 'bg-light'
  
  const classMap: Record<string, string> = {
    'fc': 'bg-danger-subtle border-danger',
    'reo': 'bg-success-subtle border-success',
    'dil': 'bg-info-subtle border-info',
    'short_sale': 'bg-warning-subtle border-warning',
    'modification': 'bg-secondary-subtle border-secondary',
    'note_sale': 'bg-primary-subtle border-primary',
  }
  return classMap[note.context_outcome] || 'bg-light'
}

// WHAT: Draft state for new note
// WHY: Store note body before submission
// HOW: Reactive refs for form binding (notes default to untagged, can be tagged via edit)
const draft = ref<string>('')
const submitting = ref<boolean>(false)

// WHAT: Edit state for inline editing
// WHY: Allow users to modify existing notes
// HOW: Track which note is being edited and its draft value (no tag editing for now)
const editingNoteId = ref<number | null>(null)
const editDraft = ref<string>('')

// WHAT: Delete confirmation modal state
// WHY: Prevent accidental deletions
// HOW: Show modal before actually deleting note
const showDeleteConfirm = ref(false)
const noteToDelete = ref<number | null>(null)
const deleting = ref(false)

/**
 * WHAT: Load all notes for this asset hub
 * WHY: Fetch complete note history for the asset
 * HOW: Call store.listNotes with assetHubId, no filters to get everything
 */
async function loadNotes() {
  await store.listNotes({
    assetHubId: props.hubId,
    // No context filters - load ALL notes for this hub
  })
}

/**
 * WHAT: Format timestamp to readable date string
 * WHY: Display user-friendly date instead of ISO string
 * HOW: Convert to localized date with short format (9/26/25)
 */
function localTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', {
      year: '2-digit',
      month: 'numeric',
      day: 'numeric',
    })
  } catch { 
    return iso 
  }
}

/**
 * WHAT: Create new note (untagged by default)
 * WHY: Add notes to master list, users can tag later via edit
 * HOW: POST to notes API with body only, context_outcome is null
 */
async function onAddNote() {
  if (!draft.value.trim()) return
  
  try {
    submitting.value = true
    
    // WHAT: Create untagged note
    // WHY: Simpler creation flow, users can categorize via edit if needed
    // HOW: Set context_outcome to null, note appears in "All Notes" filter
    await store.createNote(props.hubId, {
      body: draft.value.trim(),
      scope: 'asset', // Asset-level note (not task-specific)
      context_outcome: null,
      context_task_type: null,
      context_task_id: null,
    })
    
    // WHAT: Clear draft and reload
    // WHY: Show newly created note in list
    draft.value = ''
    await loadNotes()
  } catch (err: any) {
    console.error('Failed to create note:', err)
    alert('Failed to create note. Please try again.')
  } finally {
    submitting.value = false
  }
}

/**
 * WHAT: Start editing a note
 * WHY: Allow inline editing of note content
 * HOW: Set edit state with note data (tag editing removed - AI will auto-tag later)
 */
function startEdit(note: NoteItem) {
  editingNoteId.value = note.id
  editDraft.value = note.body
}

/**
 * WHAT: Cancel note editing
 * WHY: Discard changes and return to view mode
 * HOW: Clear edit state
 */
function cancelEdit() {
  editingNoteId.value = null
  editDraft.value = ''
}

/**
 * WHAT: Save edited note
 * WHY: Update note body (tags will be AI auto-tagged later)
 * HOW: PATCH note via store, reload to show changes
 */
async function saveEdit(noteId: number) {
  if (!editDraft.value.trim()) return
  
  try {
    // WHAT: Update note with new body only
    // WHY: Simple edit flow, tags will be managed by AI later
    // HOW: PATCH with body field only
    await store.patchNote(props.hubId, noteId, { 
      body: editDraft.value.trim(),
    })
    
    await loadNotes()
    cancelEdit()
  } catch (err: any) {
    console.error('Failed to update note:', err)
    alert('Failed to update note. Please try again.')
  }
}

/**
 * WHAT: Show delete confirmation modal
 * WHY: Confirm before deleting note
 * HOW: Set noteToDelete and show modal
 */
function deleteNote(noteId: number) {
  noteToDelete.value = noteId
  showDeleteConfirm.value = true
}

/**
 * WHAT: Cancel delete operation
 * WHY: Close modal without deleting
 * HOW: Reset delete state
 */
function cancelDelete() {
  showDeleteConfirm.value = false
  noteToDelete.value = null
  deleting.value = false
}

/**
 * WHAT: Confirm and execute note deletion
 * WHY: Remove note from database
 * HOW: DELETE via store, reload notes list
 */
async function confirmDelete() {
  if (!noteToDelete.value) return
  
  try {
    deleting.value = true
    await store.deleteNote(props.hubId, noteToDelete.value)
    await loadNotes()
    cancelDelete()
  } catch (err: any) {
    console.error('Failed to delete note:', err)
    alert('Failed to delete note. Please try again.')
    deleting.value = false
  }
}

// WHAT: Initial load and reactive reload on hub change
// WHY: Fetch notes when component mounts or asset changes
// HOW: onMounted + watch on hubId
onMounted(loadNotes)
watch(() => props.hubId, loadNotes)
</script>

<style scoped>
/* WHAT: Notes list container styles */
/* WHY: Ensure smooth scrolling and proper spacing */
.notes-list {
  padding-right: 0.25rem; /* Space for scrollbar */
}

/* WHAT: Individual note card hover effect */
/* WHY: Show edit/delete actions on hover for cleaner UI */
/* HOW: Hide actions by default, show on hover */
.note-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.note-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1) !important;
}

/* WHAT: Hide note actions by default */
/* WHY: Cleaner UI when not interacting */
/* HOW: Opacity 0 normally, opacity 1 on parent hover */
.note-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.note-card:hover .note-actions {
  opacity: 1;
}
</style>

