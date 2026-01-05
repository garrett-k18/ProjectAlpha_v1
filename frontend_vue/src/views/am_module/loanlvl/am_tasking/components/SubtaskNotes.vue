<template>
  <!--
    SubtaskNotes: Reusable notes panel for a specific subtask context.

    Documentation reviewed:
    - Pinia: https://pinia.vuejs.org/core-concepts/
    - DRF filtering guidelines: https://www.django-rest-framework.org/api-guide/filtering/
    - Hyper UI badges (styling guidance): https://hyperui.dev/components/badges

    Behavior:
    - Loads notes for the given (hubId, outcome, taskType, taskId) context.
    - Displays a simple feed with author + timestamp and body.
    - Provides a composer to add a new note with optional tag.
  -->
  <div class="card border-0 bg-body-tertiary">
    <div class="card-body p-2">
      <!--
        Notes panel with composer above the list for better UX.
        Each note entry is rendered as: "timestamp: note body - user"
        Composer allows adding new notes for this outcome context.
      -->
      <div class="d-flex align-items-center gap-2 mb-2 small text-muted">
        <i class="fas fa-note-sticky"></i>
        <span v-if="loading" class="spinner-border spinner-border-sm text-secondary me-2" role="status" aria-hidden="true"></span>
      </div>

      <!-- Composer: positioned above notes list for better UX -->
      <form class="mb-3 d-flex gap-2" @submit.prevent="onAdd">
        <textarea
          v-model="draft"
          class="form-control form-control-sm"
          rows="2"
          placeholder="Add a note..."
          aria-label="Add a note"
        ></textarea>
        <button type="submit" class="btn btn-sm btn-primary align-self-start" :disabled="submitting || !draft.trim()">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1"></span>
          Add
        </button>
      </form>

      <!-- Notes list (scrollable when long) -->
      <div class="d-flex flex-column gap-2" style="max-height: 200px; overflow: auto;">
        <div v-if="notes.length === 0" class="text-muted small">No notes yet.</div>
        <div
          v-for="n in notes"
          :key="n.id"
          class="px-2 py-1 rounded bg-light border position-relative note-item"
        >
          <!-- Edit mode -->
          <div v-if="editingNoteId === n.id" class="d-flex gap-2">
            <input
              v-model="editDraft"
              type="text"
              class="form-control form-control-sm"
              @keyup.enter="saveEdit(n.id)"
              @keyup.esc="cancelEdit"
              ref="editInput"
            />
            <button class="btn btn-sm btn-success" @click="saveEdit(n.id)" :disabled="!editDraft.trim()">
              Save
            </button>
            <button class="btn btn-sm btn-secondary" @click="cancelEdit">
              Cancel
            </button>
          </div>
          <!-- View mode -->
          <div v-else class="d-flex align-items-start justify-content-between gap-2">
            <div class="flex-grow-1 small">
              <span class="text-muted">{{ localTime(n.created_at) }}</span>
              <span class="text-muted">: </span>
              <span class="fw-bold">{{ n.body }}</span>
              <span class="text-muted"> - {{ n.created_by_username || 'User' }}</span>
            </div>
            <div class="d-flex gap-1 note-actions flex-shrink-0">
              <button class="btn btn-sm btn-outline-primary px-1 py-0" @click="startEdit(n)" title="Edit">
                <i class="mdi mdi-pencil"></i>
              </button>
              <button class="btn btn-sm btn-outline-danger px-1 py-0" @click="deleteNote(n.id)" title="Delete">
                <i class="mdi mdi-delete"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirm Delete Modal -->
  <template v-if="showDeleteConfirm">
    <!-- Backdrop behind modal -->
    <div class="modal-backdrop fade show" style="z-index: 1050;"></div>
    <!-- Modal above backdrop -->
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
// SubtaskNotes is now read-only: it displays saved notes in a compact format.
// Each variable and function includes clear comments per user preference.
import { onMounted, watch, computed, ref } from 'vue'
import { useNotesStore, type NoteItem, type OutcomeKey } from '@/stores/notes'

// Props: identify the asset (hubId), the parent outcome, and the specific task context
// When taskType and taskId are null, this shows outcome-level notes (not task-specific)
const props = withDefaults(defineProps<{
  hubId: number
  outcome: OutcomeKey
  taskType: string | null
  taskId?: number | null
}>(), {
  taskType: null,
  taskId: null,
})

// Pinia store for notes (centralized source of truth)
const store = useNotesStore()

// Loading flag derived from store state for the current hub
const loading = computed(() => store.loadingByHub[props.hubId] ?? false)
// Reactive list for this hub; filtered client-side by context
const notes = computed<NoteItem[]>(() => {
  const allNotes = store.getNotesForHub(props.hubId)
  // Filter by context: outcome, taskType, taskId
  return allNotes.filter(n => {
    if (n.context_outcome !== props.outcome) return false
    if (props.taskType !== null && n.context_task_type !== props.taskType) return false
    if (props.taskId !== null && n.context_task_id !== props.taskId) return false
    if (props.taskType === null && n.context_task_type !== null) return false
    if (props.taskId === null && n.context_task_id !== null) return false
    return true
  })
})

// Helper to convert ISO timestamp to a localized, human-friendly date string
// Keep it very compact: date only with 2-digit year (e.g., "9/26/25")
function localTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', {
      year: '2-digit',
      month: 'numeric',
      day: 'numeric',
    })
  } catch { return iso }
}

// Load ALL notes for this hub (no filters) so we can filter client-side
// WHY: Allows multiple SubtaskNotes components to share the same cache
// HOW: Load once, filter in computed property based on context
async function loadNotes() {
  await store.listNotes({
    assetHubId: props.hubId,
    // No context filters - load all notes for this hub
  })
}

// Draft state for new note and submission flag for UX feedback
const draft = ref<string>('')
const submitting = ref<boolean>(false)

// Edit state for inline editing
const editingNoteId = ref<number | null>(null)
const editDraft = ref<string>('')

// Delete confirmation modal state
const showDeleteConfirm = ref(false)
const noteToDelete = ref<number | null>(null)
const deleting = ref(false)

// Start editing a note
function startEdit(note: NoteItem) {
  editingNoteId.value = note.id
  editDraft.value = note.body
}

// Cancel editing
function cancelEdit() {
  editingNoteId.value = null
  editDraft.value = ''
}

// Save edited note
async function saveEdit(noteId: number) {
  if (!editDraft.value.trim()) return
  try {
    await store.patchNote(props.hubId, noteId, { body: editDraft.value.trim() })
    await loadNotes()
    cancelEdit()
  } catch (err) {
    console.error('Failed to update note:', err)
    alert('Failed to update note. Please try again.')
  }
}

// Show delete confirmation modal
function deleteNote(noteId: number) {
  noteToDelete.value = noteId
  showDeleteConfirm.value = true
}

// Cancel delete
function cancelDelete() {
  showDeleteConfirm.value = false
  noteToDelete.value = null
  deleting.value = false
}

// Confirm and execute delete
async function confirmDelete() {
  if (!noteToDelete.value) return
  try {
    deleting.value = true
    await store.deleteNote(props.hubId, noteToDelete.value)
    await loadNotes()
    cancelDelete()
  } catch (err) {
    console.error('Failed to delete note:', err)
    alert('Failed to delete note. Please try again.')
    deleting.value = false
  }
}

// Create a new note for this specific subtask context, then refresh the list
async function onAdd() {
  if (!draft.value.trim()) return
  try {
    submitting.value = true
    await store.createNote(props.hubId, {
      body: draft.value.trim(),
      scope: 'task',
      context_outcome: props.outcome,
      context_task_type: props.taskType,
      context_task_id: props.taskId ?? null,
    })
    draft.value = ''
    await loadNotes()
  } finally {
    submitting.value = false
  }
}

// Initial load and reactive reload on relevant prop changes
onMounted(loadNotes)
watch(() => [props.hubId, props.outcome, props.taskType, props.taskId], loadNotes)
</script>

<style scoped>
/* Keep styles minimal and rely on Bootstrap/Hyper UI for consistency */
.card { border-radius: 0.375rem; }
.text-body { white-space: pre-wrap; }

/* Always show edit/delete actions for better UX */
.note-actions {
  min-width: 80px;
}
</style>
