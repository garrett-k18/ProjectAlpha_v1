<template>
  <!--
    DocumentsQuickView
    - Reusable, Hyper-UI-styled card to show a compact list of documents.
    - Designed for use in modals (loan-level) and full pages.
    - Accepts pre-fetched `docs` via props so it does not depend on any API shape.
  -->
  <div class="card h-100 d-flex flex-column">
    <!-- Header aligned with other dashboard cards -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
      <div class="d-flex align-items-center gap-2">
        <slot name="actions">
          <router-link
            v-if="showViewAll && viewAllTo"
            :to="viewAllTo"
            class="btn btn-sm btn-outline-primary"
          >
            View All
          </router-link>
        </slot>
      </div>
    </div>
    <!-- Body: per-item cards matching Hyper UI Files pattern -->
    <div class="card-body pt-0">
      <!-- Loading skeletons -->
      <div v-if="loading" class="">
        <div v-for="n in 3" :key="n" class="card mb-1 shadow-none border">
          <div class="p-2">
            <div class="row align-items-center">
              <div class="col col-auto">
                <div class="avatar-sm">
                  <span class="avatar-title rounded placeholder col-6">&nbsp;</span>
                </div>
              </div>
              <div class="col ps-0">
                <div class="placeholder-glow">
                  <span class="placeholder col-6"></span>
                </div>
                <p class="mb-0 placeholder-glow"><span class="placeholder col-3"></span></p>
              </div>
              <div class="col col-auto">
                <a class="btn btn-link btn-lg text-muted disabled" aria-disabled="true"><i class="ri-download-2-line"></i></a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Items -->
      <template v-else-if="itemsToRender.length">
        <div
          v-for="doc in itemsToRender"
          :key="doc.id"
          class="card mb-1 shadow-none border"
        >
          <div class="p-2">
            <div class="row align-items-center">
              <!-- Avatar / thumbnail -->
              <div class="col col-auto">
                <div class="avatar-sm">
                  <template v-if="isImageType(doc) && doc.thumbnailUrl">
                    <img :src="doc.thumbnailUrl" class="avatar-sm rounded" :alt="doc.name" />
                  </template>
                  <template v-else>
                    <span class="avatar-title rounded" :class="avatarBgClass(doc)">{{ extLabel(doc) }}</span>
                  </template>
                </div>
              </div>

              <!-- Name and size -->
              <div class="col ps-0">
                <a :href="doc.previewUrl || doc.downloadUrl || '#'" class="text-muted fw-bold" :title="doc.name">
                  {{ doc.name }}
                </a>
                <p class="mb-0">{{ doc.sizeBytes != null ? formatSize(doc.sizeBytes) : '' }}</p>
              </div>

              <!-- Download button -->
              <div class="col col-auto">
                <a
                  v-if="doc.downloadUrl"
                  :href="doc.downloadUrl"
                  class="btn btn-link btn-lg text-muted"
                  title="Download"
                  aria-label="Download"
                >
                  <i class="ri-download-2-line"></i>
                </a>
                <a
                  v-else
                  :href="doc.previewUrl || '#'"
                  class="btn btn-link btn-lg text-muted"
                  title="Open"
                  aria-label="Open"
                >
                  <i class="ri-external-link-line"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty state -->
      <div v-else class="text-center text-muted small">
        No documents available.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ----------------------------------------------------------------------------------
// DocumentsQuickView.vue
// ----------------------------------------------------------------------------------
// This component is data-agnostic: pass a normalized array of `DocumentItem` via props.
// It intentionally does not fetch from an API to remain reusable across pages/tabs.
// If a future API is added, the parent can fetch and pass the results here.
// ----------------------------------------------------------------------------------

import { computed } from 'vue'

/**
 * DocumentItem
 * - Generic shape for a document row used by the quick view widget.
 * - Parents can adapt backend data to this shape before passing to the component.
 */
export interface DocumentItem {
  /** Stable identifier for rendering lists */
  id: string | number
  /** Display name of the document (e.g., "Broker BPO.pdf") */
  name: string
  /** Optional type/extension (e.g., 'pdf', 'docx', 'image/jpeg') */
  type?: string | null
  /** Optional file size in bytes */
  sizeBytes?: number | null
  /** Optional last updated timestamp (ISO string) */
  updatedAt?: string | null
  /** Optional preview URL (opens in new tab) */
  previewUrl?: string | null
  /** Optional direct download URL */
  downloadUrl?: string | null
  /** Optional thumbnail URL for images (small preview used in avatar) */
  thumbnailUrl?: string | null
}

export interface DocumentsQuickViewProps {
  /** Card title text */
  title?: string
  /** Array of documents to render (already normalized) */
  docs?: DocumentItem[]
  /** Limit the number of items shown (set to 0 or null to disable limiting) */
  maxItems?: number | null
  /** Show built-in View All button when a route is provided */
  showViewAll?: boolean
  /** Route location for the View All action (optional) */
  viewAllTo?: string | null
  /** Show loading placeholders */
  loading?: boolean
}

const props = withDefaults(defineProps<DocumentsQuickViewProps>(), {
  title: 'Documents',
  docs: () => [],
  maxItems: 5,
  showViewAll: true,
  viewAllTo: null,
  loading: false,
})

// Compute array truncated by maxItems (if provided)
const itemsToRender = computed<DocumentItem[]>(() => {
  const arr = props.docs || []
  if (!props.maxItems || props.maxItems <= 0) return arr
  return arr.slice(0, props.maxItems)
})

// --- Helper: format bytes to human readable size ---
function formatSize(bytes?: number | null): string {
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

// --- Helper: determine if item is an image (by MIME or extension) ---
function isImageType(doc: DocumentItem): boolean {
  const t = (doc.type || '').toLowerCase()
  if (t.includes('image/')) return true
  const name = (doc.name || '').toLowerCase()
  return name.endsWith('.png') || name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.gif') || name.endsWith('.webp')
}

// --- Helper: short uppercase extension label (e.g., .ZIP, .PDF, .MP4) ---
function extLabel(doc: DocumentItem): string {
  const name = doc.name || ''
  const dot = name.lastIndexOf('.')
  if (dot === -1) return 'FILE'
  return `.${name.substring(dot + 1).toUpperCase()}`
}

// --- Helper: avatar background class per file family ---
function avatarBgClass(doc: DocumentItem): string {
  const label = extLabel(doc)
  if (label.includes('PDF')) return 'text-bg-danger'
  if (label.includes('DOC') || label.includes('DOCX')) return 'text-bg-primary'
  if (label.includes('XLS') || label.includes('XLSX')) return 'text-bg-success'
  if (label.includes('PNG') || label.includes('JPG') || label.includes('JPEG') || label.includes('GIF')) return 'text-bg-info'
  if (label.includes('ZIP') || label.includes('RAR') || label.includes('7Z')) return 'text-bg-primary'
  if (label.includes('MP4') || label.includes('MOV') || label.includes('AVI')) return 'text-bg-secondary'
  return 'text-bg-secondary'
}
</script>

<style scoped>
/* Keep styles minimal; rely on Bootstrap/Hyper UI utility classes. */
</style>
