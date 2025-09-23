<template>
  <div class="card w-100 d-flex flex-column">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title mb-0">Notes</h4>
    </div>
    <div class="card-body pt-2">
      <!-- Bubble editor for composing a new note -->
      <div class="mb-3">
        <QuillEditor
          theme="bubble"
          content-type="html"
          v-model:content="editorHtml"
          :toolbar="toolbarBubble"
          style="min-height: 120px"
        />
        <div class="d-flex gap-2 mt-2">
          <b-button size="sm" variant="primary" :disabled="saving || !canSubmit" @click="submitNote">
            <span v-if="!saving">Save Note</span>
            <span v-else>Saving…</span>
          </b-button>
          <b-button size="sm" variant="outline-secondary" :disabled="saving" @click="clearEditor">Clear</b-button>
        </div>
      </div>

      <!-- Notes list: scrollable, timestamped, user stamped -->
      <div class="border rounded notes-list" style="max-height: 300px; overflow: auto;">
        <div v-if="loading" class="p-3 text-muted small">Loading notes…</div>
        <div v-else-if="notes.length === 0" class="p-3 text-muted small">No notes yet.</div>
        <ul v-else class="list-unstyled mb-0">
          <li v-for="n in notes" :key="n.id" class="note-item border-bottom">
            <div class="d-flex justify-content-between align-items-center mb-1 meta">
              <div class="text-muted">
                <span class="fw-semibold text-dark">{{ n.created_by_username || 'Unknown' }}</span>
                • {{ formatDateTime(n.created_at) }}
              </div>
              <div class="d-flex align-items-center gap-2">
                <span v-if="n.tag" class="badge bg-light text-dark border fw-normal">{{ displayTag(n.tag) }}</span>
                <b-button size="sm" variant="outline-secondary" @click="startEdit(n)" v-if="editingId !== n.id">Edit</b-button>
                <b-button size="sm" variant="outline-danger" @click="openConfirmDelete(n)">Delete</b-button>
              </div>
            </div>
            <div v-if="editingId === n.id" class="mb-2">
              <QuillEditor
                theme="bubble"
                content-type="html"
                v-model:content="editHtml"
                :toolbar="toolbarBubble"
                style="min-height: 100px"
              />
              <div class="d-flex gap-2 mt-2">
                <b-button size="sm" variant="primary" :disabled="savingEdit" @click="saveEdit(n)">Save</b-button>
                <b-button size="sm" variant="outline-secondary" :disabled="savingEdit" @click="cancelEdit">Cancel</b-button>
              </div>
            </div>
            <div v-else class="note-body" v-html="n.body"></div>
          </li>
        </ul>
      </div>
    </div>
    
    <!-- Delete confirmation modal (Hyper/BootstrapVue Next) -->
    <b-modal v-model="confirmVisible" title="Delete Note?" centered hide-footer>
      <div class="mb-3">Are you sure you want to delete this note?</div>
      <div class="border rounded p-2 bg-light-subtle small mb-3" v-if="noteToDelete">
        <div class="text-muted mb-1">
          <span class="fw-semibold text-dark">{{ noteToDelete.created_by_username || 'Unknown' }}</span>
          • {{ formatDateTime(noteToDelete.created_at) }}
        </div>
        <div class="note-body" v-html="noteToDelete.body"></div>
      </div>
      <div class="d-flex justify-content-end gap-2">
        <b-button size="sm" variant="outline-secondary" @click="confirmVisible=false" :disabled="deleting">Cancel</b-button>
        <b-button size="sm" variant="danger" @click="performDelete" :disabled="deleting">
          <span v-if="!deleting">Delete</span>
          <span v-else>Deleting…</span>
        </b-button>
      </div>
    </b-modal>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, onMounted, watch } from 'vue'
import { BModal } from 'bootstrap-vue-next'
import { QuillEditor } from '@vueup/vue-quill'
import http from '@/lib/http'

export type ServicingNoteItem = {
  id: number
  body: string
  tag: string | null
  pinned?: boolean
  created_at: string
  updated_at: string
  created_by: number | null
  updated_by: number | null
  created_by_username?: string | null
  updated_by_username?: string | null
}

const props = withDefaults(defineProps<{ assetId?: number | null }>(), { assetId: null })

// Quill bubble toolbar (inline minimal)
const toolbarBubble = [
  ['bold', 'italic', 'underline', 'strike'],
  [{ header: 1 }, { header: 2 }],
  [{ list: 'ordered' }, { list: 'bullet' }],
  ['link'],
]

const notes = ref<ServicingNoteItem[]>([])
const loading = ref(false)
const saving = ref(false)
const editorHtml = ref('')
const editingId = ref<number | null>(null)
const savingEdit = ref(false)
const editHtml = ref('')
const confirmVisible = ref(false)
const noteToDelete = ref<ServicingNoteItem | null>(null)
const deleting = ref(false)

const canSubmit = computed(() => editorHtml.value && editorHtml.value.replace(/<[^>]*>/g, '').trim().length > 0)

function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch {
    return iso
  }
}

function displayTag(tag?: string | null): string {
  if (!tag) return ''
  const map: Record<string, string> = { urgent: 'Urgent', legal: 'Legal', qc: 'Quality Control', ops: 'Operations', info: 'Info' }
  return map[tag] || tag
}

async function loadNotes() {
  if (!props.assetId) return
  loading.value = true
  try {
    const res = await http.get(`/am/assets/${props.assetId}/notes/`)
    notes.value = Array.isArray(res.data) ? res.data : []
  } catch {
    notes.value = []
  } finally {
    loading.value = false
  }
}

async function submitNote() {
  if (!props.assetId || !canSubmit.value) return
  saving.value = true
  try {
    const payload = { body: editorHtml.value }
    const res = await http.post(`/am/assets/${props.assetId}/notes/`, payload)
    if (res && res.data) notes.value = [res.data as ServicingNoteItem, ...notes.value]
    editorHtml.value = ''
  } catch {
    // non-fatal in dev
  } finally {
    saving.value = false
  }
}

function clearEditor() {
  editorHtml.value = ''
}

onMounted(loadNotes)
watch(() => props.assetId, () => loadNotes())

function startEdit(n: ServicingNoteItem) {
  editingId.value = n.id
  editHtml.value = n.body || ''
}

function cancelEdit() {
  editingId.value = null
  editHtml.value = ''
}

async function saveEdit(n: ServicingNoteItem) {
  if (!editingId.value) return
  savingEdit.value = true
  try {
    const payload = { body: editHtml.value }
    const res = await http.patch(`/am/notes/${n.id}/`, payload)
    // Update in-place
    const idx = notes.value.findIndex(x => x.id === n.id)
    if (idx !== -1) notes.value[idx] = { ...notes.value[idx], ...(res.data as ServicingNoteItem) }
    cancelEdit()
  } catch {
    // non-fatal in dev
  } finally {
    savingEdit.value = false
  }
}

function openConfirmDelete(n: ServicingNoteItem) {
  noteToDelete.value = n
  confirmVisible.value = true
}

async function performDelete() {
  if (!noteToDelete.value) return
  deleting.value = true
  try {
    await http.delete(`/am/notes/${noteToDelete.value.id}/`)
    notes.value = notes.value.filter(x => x.id !== noteToDelete.value!.id)
    confirmVisible.value = false
    noteToDelete.value = null
  } catch {
    // non-fatal in dev
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.note-body :deep(p) { margin-bottom: 0.5rem; }
.note-body :deep(h1), .note-body :deep(h2) { margin: 0.25rem 0; font-size: 1.1rem; }
.notes-list { font-size: 0.875rem; }
.note-item { padding: 0.5rem 0.75rem; }
.note-item .meta { font-size: 0.78rem; }
.note-body { line-height: 1.2; }
.note-body :deep(p:last-child) { margin-bottom: 0; }
.note-body :deep(img),
.note-body :deep(video),
.note-body :deep(iframe) { max-width: 100%; height: auto; display: block; }
</style>
