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
      <!-- Header row with small title and optional loading indicator -->
      <div class="d-flex align-items-center justify-content-between mb-2">
        <div class="small text-muted d-flex align-items-center gap-2">
          <i class="fas fa-note-sticky"></i>
          <span>Notes</span>
          <span v-if="loading" class="spinner-border spinner-border-sm text-secondary" role="status" aria-hidden="true"></span>
        </div>
        <div class="d-flex align-items-center gap-1">
          <!-- Tag filter (local, optional future enhancement) -->
        </div>
      </div>

      <!-- Notes list; compact layout with author + time + tag pill -->
      <div class="d-flex flex-column gap-2 mb-2" style="max-height: 200px; overflow: auto;">
        <div v-if="notes.length === 0" class="text-muted small">No notes yet. Add one below.</div>
        <div v-for="n in notes" :key="n.id" class="p-2 border rounded bg-white">
          <div class="d-flex align-items-center justify-content-between mb-1">
            <div class="small text-muted">
              <strong>{{ n.created_by_username || 'User' }}</strong>
              <span class="ms-1">•</span>
              <span class="ms-1">{{ localTime(n.created_at) }}</span>
            </div>
            <UiBadge v-if="n.tag" :tone="tagTone(n.tag)" size="sm">{{ tagLabel(n.tag) }}</UiBadge>
          </div>
          <div class="text-body">{{ n.body }}</div>
        </div>
      </div>

      <!-- Composer: textarea + tag select + add button -->
      <form class="d-flex flex-column gap-2" @submit.prevent="onAdd">
        <div class="row g-2">
          <div class="col-9">
            <textarea
              v-model="draft"
              class="form-control"
              rows="2"
              placeholder="Add a note..."
            ></textarea>
          </div>
          <div class="col-3">
            <select v-model="draftTag" class="form-select">
              <option :value="null">No tag</option>
              <option value="urgent">Urgent</option>
              <option value="legal">Legal</option>
              <option value="qc">Quality Control</option>
              <option value="ops">Operations</option>
              <option value="info">Info</option>
            </select>
          </div>
        </div>
        <div class="d-flex align-items-center justify-content-end">
          <button type="submit" class="btn btn-sm btn-primary" :disabled="submitting || !draft.trim()">
            <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
            Add Note
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
// SubtaskNotes props define the context for listing and creating notes.
// Each variable and function includes clear comments per user preference.
import { onMounted, watch, computed, ref, withDefaults, defineProps } from 'vue'
import UiBadge from '@/components/ui/UiBadge.vue'
import { useNotesStore, type NoteItem, type NoteTag, type OutcomeKey } from '@/stores/notes'

// Props: identify the asset (hubId), the parent outcome, and the specific task context
const props = withDefaults(defineProps<{
  hubId: number
  outcome: OutcomeKey
  taskType: string
  taskId?: number | null
}>(), {
  taskId: null,
})

// Pinia store for notes
const store = useNotesStore()

// Local reactive state for loading/submission and the draft values
const loading = computed(() => store.loadingByHub[props.hubId] ?? false)
const notes = computed<NoteItem[]>(() => store.getNotesForHub(props.hubId))
const draft = ref<string>('')          // user-entered note text before create
const draftTag = ref<NoteTag>(null)    // optional tag selected in composer
const submitting = ref<boolean>(false) // indicates when a create request is in flight

// Helper to convert ISO timestamp to a localized, human-friendly date string
function localTime(iso: string): string {
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

// Map backend tag keys to a readable label for display inside UiBadge
function tagLabel(tag: NoteTag): string {
  const labels: Record<NonNullable<NoteTag>, string> = {
    urgent: 'Urgent',
    legal: 'Legal',
    qc: 'Quality Control',
    ops: 'Operations',
    info: 'Info',
  }
  return tag ? labels[tag] : ''
}

// Tone mapping for tags using badge token keys defined in badgeTokens
function tagTone(tag: NoteTag): import('@/config/badgeTokens').BadgeToneKey {
  const tones: Record<NonNullable<NoteTag>, import('@/config/badgeTokens').BadgeToneKey> = {
    urgent: 'danger',
    legal: 'secondary',
    qc: 'info',
    ops: 'primary',
    info: 'success',
  }
  return tag ? tones[tag] : 'secondary'
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

// Handle adding a new note using the composer
async function onAdd() {
  if (!draft.value.trim()) return
  try {
    submitting.value = true
    await store.createNote(props.hubId, {
      body: draft.value.trim(),
      tag: draftTag.value ?? undefined,
      scope: 'task',
      context_outcome: props.outcome,
      context_task_type: props.taskType,
      context_task_id: props.taskId ?? null,
    })
    draft.value = ''
    draftTag.value = null
    // Refresh the list to reflect new sorting from the backend
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
