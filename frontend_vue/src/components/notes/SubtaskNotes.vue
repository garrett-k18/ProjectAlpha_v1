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
        Compact list of notes. Each entry is rendered as a single line in the format:
        "timestamp: note body - user"
        The composer has been intentionally removed per request.
      -->
      <div class="d-flex align-items-center gap-2 mb-2 small text-muted">
        <i class="fas fa-note-sticky"></i>
        <span>Notes</span>
        <span v-if="loading" class="spinner-border spinner-border-sm text-secondary" role="status" aria-hidden="true"></span>
      </div>

      <!-- Notes list (scrollable when long) -->
      <div class="d-flex flex-column gap-2" style="max-height: 200px; overflow: auto;">
        <div v-if="notes.length === 0" class="text-muted small">No notes yet.</div>
        <div
          v-for="n in notes"
          :key="n.id"
          class="px-1 py-0 rounded bg-transparent text-body small"
        >
          <span>{{ localTime(n.created_at) }}</span>
          <span>: </span>
          <span class="fw-bold">{{ n.body }}</span>
          <span> - {{ n.created_by_username || 'User' }}</span>
        </div>
      </div>

      <!-- Composer: restored per request. Allows adding a new note while keeping list formatting above. -->
      <form class="mt-2 d-flex gap-2" @submit.prevent="onAdd">
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
    </div>
  </div>
</template>

<script setup lang="ts">
// SubtaskNotes is now read-only: it displays saved notes in a compact format.
// Each variable and function includes clear comments per user preference.
import { onMounted, watch, computed, withDefaults, defineProps, ref } from 'vue'
import { useNotesStore, type NoteItem, type OutcomeKey } from '@/stores/notes'

// Props: identify the asset (hubId), the parent outcome, and the specific task context
const props = withDefaults(defineProps<{
  hubId: number
  outcome: OutcomeKey
  taskType: string
  taskId?: number | null
}>(), {
  taskId: null,
})

// Pinia store for notes (centralized source of truth)
const store = useNotesStore()

// Loading flag derived from store state for the current hub
const loading = computed(() => store.loadingByHub[props.hubId] ?? false)
// Reactive list for this hub; server-side filters applied in loadNotes()
const notes = computed<NoteItem[]>(() => store.getNotesForHub(props.hubId))

// Helper to convert ISO timestamp to a localized, human-friendly date string
// Keep it very compact: date only with 2-digit year (e.g., "9/26/25")
function localTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString(undefined, {
      year: '2-digit',
      month: 'numeric',
      day: 'numeric',
    })
  } catch { return iso }
}

// Load notes for the current context (asset + outcome + task type + optional task id)
async function loadNotes() {
  await store.listNotes({
    assetHubId: props.hubId,
    contextOutcome: props.outcome,
    contextTaskType: props.taskType,
    contextTaskId: props.taskId ?? undefined,
  })
}

// Draft state for new note and submission flag for UX feedback
const draft = ref<string>('')
const submitting = ref<boolean>(false)

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
</style>
