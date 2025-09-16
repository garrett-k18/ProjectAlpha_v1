<template>
  <!--
    TradeDocumentsModal
    - Shows a two-pane layout: a document list on the left and a preview/viewer on the right.
    - The list is simple and uses Bootstrap/Hyper UI classes (no custom CSS beyond utilities).
    - Clicking an item selects it and updates the viewer.
  -->
  <div class="container-fluid">
    <div class="row g-3">
      <!-- Left: documents list -->
      <div class="col-12 col-xl-4 col-lg-5">
        <div class="card h-100 d-flex flex-column">
          <div class="d-flex card-header justify-content-between align-items-center">
            <h4 class="header-title mb-0">Documents</h4>
          </div>
          <div class="card-body pt-0 overflow-auto" style="max-height: 60vh">
            <!-- Loading state -->
            <div v-if="loading" class="text-center text-muted py-4">
              <div class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div>
              <div class="mt-2">Loading…</div>
            </div>

            <!-- Items -->
            <div v-else>
              <div
                v-for="doc in docs"
                :key="doc.id"
                class="card mb-1 shadow-none border"
                :class="{ 'border-primary': isActive(doc) }"
                role="button"
                @click="select(doc)"
                @keydown.enter="select(doc)"
                tabindex="0"
              >
                <div class="p-2 d-flex align-items-center">
                  <!-- Icon / thumbnail -->
                  <div class="me-2">
                    <span class="avatar-title rounded px-2 py-1 small" :class="avatarBgClass(doc)">{{ extLabel(doc) }}</span>
                  </div>
                  <!-- Name -->
                  <div class="flex-grow-1">
                    <div class="fw-semibold text-truncate" :title="doc.name">{{ doc.name }}</div>
                    <div class="small text-muted">{{ doc.sizeBytes != null ? formatSize(doc.sizeBytes) : '' }}</div>
                  </div>
                  <!-- Download -->
                  <div>
                    <a v-if="doc.downloadUrl" :href="doc.downloadUrl" class="btn btn-link btn-sm text-muted" title="Download" @click.stop>
                      <i class="ri-download-2-line"></i>
                    </a>
                  </div>
                </div>
              </div>

              <div v-if="!docs || !docs.length" class="text-center text-muted small py-3">
                Documents coming soon.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: viewer -->
      <div class="col-12 col-xl-8 col-lg-7">
        <div class="card h-100 d-flex flex-column">
          <div class="d-flex card-header justify-content-between align-items-center">
            <h4 class="header-title mb-0">Viewer</h4>
            <div class="d-flex align-items-center gap-2">
              <a v-if="active?.downloadUrl && isValidUrl(active.downloadUrl as string)" :href="active.downloadUrl as string" class="btn btn-sm btn-outline-secondary">
                <i class="ri-download-2-line me-1"></i> Download
              </a>
              <a v-if="activeUrl" :href="activeUrl" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">
                <i class="ri-external-link-line me-1"></i> Open
              </a>
            </div>
          </div>
          <div class="card-body p-2" style="min-height: 60vh">
            <!-- Coming soon placeholder (no docs or invalid URLs) -->
            <div v-if="!active || !activeUrl" class="h-100 d-flex align-items-center justify-content-center text-center text-muted">
              <div>
                <i class="ri-file-list-3-line display-6 d-block mb-2"></i>
                Documents coming soon.
              </div>
            </div>

            <!-- Image preview (only when we have a valid URL) -->
            <div v-else-if="isImageType(active)" class="h-100 d-flex align-items-center justify-content-center">
              <img :src="activeUrl" :alt="active.name" class="img-fluid rounded shadow-sm" />
            </div>

            <!-- PDF preview (only when we have a valid URL) -->
            <div v-else-if="isPdfType(active)" class="h-100">
              <object :data="activeUrl" type="application/pdf" width="100%" height="100%">
                <div class="h-100 d-flex align-items-center justify-content-center text-muted">
                  PDF preview unavailable. Use Open or Download.
                </div>
              </object>
            </div>

            <!-- Fallback content -->
            <div v-else class="h-100 d-flex align-items-center justify-content-center text-center text-muted p-3">
              <div>
                <div class="mb-2">Preview not available for this file type.</div>
                <div>
                  <a v-if="activeUrl" :href="activeUrl" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary">
                    <i class="ri-external-link-line me-1"></i> Open
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// TradeDocumentsModal.vue
// ----------------------------------------------------------------------------------
// This modal body is UI-only (no fetching). The parent passes `docs` already
// normalized to the shared `DocumentItem` shape from DocumentsQuickView.vue.
// We maintain an internal `active` selection and provide previews for common
// types (images, PDFs). For other types, we show Open/Download actions.
// ----------------------------------------------------------------------------------
import { ref, watch, computed } from 'vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'

// Props: list and loading flag (parent may control loading state)
const props = defineProps<{ docs: DocumentItem[]; loading?: boolean }>()

// Reactive selection for the currently active document
const activeId = ref<string | number | null>(null)

// Compute the active document based on `activeId`
const active = computed<DocumentItem | null>(() => {
  return (props.docs || []).find(d => String(d.id) === String(activeId.value)) || null
})

// Treat empty string or '#' as invalid URLs to avoid embedding the dashboard
function isValidUrl(u?: string | null): boolean {
  return !!u && u !== '#'
}

// Consolidated URL for viewer usage (prefers previewUrl, falls back to downloadUrl)
const activeUrl = computed<string | null>(() => {
  const u = (active.value?.previewUrl || active.value?.downloadUrl || null) as string | null
  return isValidUrl(u) ? u : null
})

// When docs change, set a sensible default selection (first item)
watch(
  () => props.docs,
  (arr) => {
    if (arr && arr.length) {
      activeId.value = arr[0].id
    } else {
      activeId.value = null
    }
  },
  { immediate: true }
)

// Helper: select an item
function select(doc: DocumentItem) {
  // Update active id when a list item is clicked
  activeId.value = doc.id
}

// Helper: check if an item is the active one (for styling)
function isActive(doc: DocumentItem): boolean {
  return String(doc.id) === String(activeId.value)
}

// -------------------------
// Rendering helpers
// -------------------------
function formatSize(bytes?: number | null): string {
  // Human readable file size (same logic pattern as DocumentsQuickView)
  if (bytes == null || isNaN(bytes as any)) return ''
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let n = Number(bytes)
  let i = 0
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024
    i++
  }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`
}

function extLabel(doc: DocumentItem): string {
  // Returns uppercase extension (e.g., .PDF)
  const name = doc.name || ''
  const dot = name.lastIndexOf('.')
  if (dot === -1) return 'FILE'
  return `.${name.substring(dot + 1).toUpperCase()}`
}

function avatarBgClass(doc: DocumentItem): string {
  // Background class per file type family (Bootstrap contextual backgrounds)
  const label = extLabel(doc)
  if (label.includes('PDF')) return 'text-bg-danger'
  if (label.includes('DOC') || label.includes('DOCX')) return 'text-bg-primary'
  if (label.includes('XLS') || label.includes('XLSX')) return 'text-bg-success'
  if (label.includes('PNG') || label.includes('JPG') || label.includes('JPEG') || label.includes('GIF')) return 'text-bg-info'
  if (label.includes('ZIP') || label.includes('RAR') || label.includes('7Z')) return 'text-bg-primary'
  if (label.includes('MP4') || label.includes('MOV') || label.includes('AVI')) return 'text-bg-secondary'
  return 'text-bg-secondary'
}

function isImageType(doc?: DocumentItem | null): boolean {
  // Determines image-type by MIME or file extension
  if (!doc) return false
  const t = (doc.type || '').toLowerCase()
  if (t.includes('image/')) return true
  const name = (doc.name || '').toLowerCase()
  return name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.gif') || name.endsWith('.webp')
}

function isPdfType(doc?: DocumentItem | null): boolean {
  if (!doc) return false
  const t = (doc.type || '').toLowerCase()
  if (t.includes('application/pdf')) return true
  const name = (doc.name || '').toLowerCase()
  return name.endsWith('.pdf')
}
</script>

<style scoped>
/* Use container utilities rather than custom CSS; keep styles minimal */
</style>
