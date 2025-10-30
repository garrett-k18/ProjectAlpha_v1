<template>
  <!-- Snapshot Tab: Embedded in modal, no Layout/Breadcrumb wrappers -->
  <div>
    <!-- Widgets Row -->
    <LoanlvlWidgets :row="row" class="mb-2" />

    <!-- Top Row: Summary, Photos, Map -->
    <b-row class="g-3 mb-3 align-items-stretch">
      <!-- Asset Summary -->
      <b-col lg="4" class="d-flex">
        <QuickSummary
          class="w-100 snapshot-card"
          :context="quickSummaryContext"
          :max-bullets="4"
          :lazy="true"
          title="Asset Summary"
        />
      </b-col>

      <!-- Photo Carousel -->
      <b-col lg="4" class="d-flex">
        <div class="card w-100 snapshot-card">
          <div class="card-body d-flex flex-column p-0">
            <PhotoCarousel
              v-if="imagesToShow.length > 0"
              class="flex-fill"
              :images="imagesToShow"
              :force-show-controls="true"
              :force-show-thumbnails="true"
              :loop="true"
              :show-thumbnails="true"
              :interval="0"
              :thumb-width="90"
              :thumb-height="50"
            />
            <div v-else class="flex-fill d-flex align-items-center justify-content-center text-muted">
              No Photos
            </div>
          </div>
        </div>
      </b-col>

      <!-- Property Map -->
      <b-col lg="4" class="d-flex">
        <PropertyMap
          class="w-100 snapshot-card"
          :row="row"
          :assetHubId="assetId"
          :zoom="15"
          :showMarker="true"
        />
      </b-col>
    </b-row>

    <!-- Bottom Row: Valuation Matrix and Documents -->
    <b-row class="g-3 align-items-stretch">
      <!-- Valuation Matrix -->
      <b-col lg="9" class="d-flex">
        <ValuationMatrixOption2 class="w-100" :row="row" :assetId="assetId" />
      </b-col>

      <!-- Documents Quick View -->
      <b-col lg="3" class="d-flex">
        <DocumentsQuickView
          class="w-100"
          title="Document Quick View"
          :docs="docItems"
          :maxItems="5"
          :showViewAll="false"
        />
      </b-col>
    </b-row>
  </div>
</template>

<script setup lang="ts">
/**
 * SnapshotTab.vue
 * 
 * Snapshot tab content for loan-level product details modal.
 * Displays asset summary, photos, map, valuation matrix, and documents.
 * Designed to be embedded in modals (no Layout/Breadcrumb wrappers).
 */
import PhotoCarousel from '@/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/components/PhotoCarousel.vue'
import PropertyMap from '@/components/PropertyMap.vue'
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'
import QuickSummary from '@/components/QuickSummary.vue'
import ValuationMatrixOption2 from '@/views/acq_module/loanlvl/components/valuationMatrix_Option2.vue'
import LoanlvlWidgets from '@/components/widgets/loanlvl-widgets.vue'

import { withDefaults, defineProps, ref, computed, watch } from 'vue'
import http from '@/lib/http'

// Props definition
const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
  module?: 'acq' | 'am'
}>(), {
  row: null,
  assetId: null,
  module: 'acq',
})

// Photo state and computed properties
const fetchedImages = ref<PhotoItem[]>([])
const imagesToShow = computed<PhotoItem[]>(() => fetchedImages.value || [])

// Reserve space for thumbnails in carousel container
const carouselContainerHeight = computed<string>(() => {
  const hasThumbs = imagesToShow.value.length >= 1
  const thumbH = 50
  const gutter = 8
  return hasThumbs ? `calc(100% - ${thumbH + gutter}px)` : '100%'
})

// Determine asset ID for photo loading (assetId prop -> row.id -> null)
const sourceId = computed<number | null>(() => {
  const idFromProduct = props.assetId != null ? Number(props.assetId) : null
  const idFromRow = (props.row && props.row.id != null) ? Number(props.row.id) : null
  return idFromProduct ?? idFromRow ?? null
})

// Fetch photos from backend
async function loadPhotos(id: number) {
  try {
    const url = props.module === 'am' ? `/am/assets/${id}/photos/` : `/acq/photos/${id}/`
    const res = await http.get(url)
    fetchedImages.value = (res.data || []) as PhotoItem[]
  } catch (err) {
    console.warn('Failed to load photos for id', id, 'module=', props.module, err)
    fetchedImages.value = []
  }
}

// Watch for asset ID changes and load photos
watch(sourceId, (id) => {
  if (id && !Number.isNaN(id)) {
    loadPhotos(id)
  } else {
    fetchedImages.value = []
  }
}, { immediate: true })

// Documents quick view data (placeholder until backend endpoint is wired)
const docItems = computed<DocumentItem[]>(() => [
  {
    id: 'pdf-bpo',
    name: 'BPO.pdf',
    type: 'application/pdf',
    sizeBytes: Math.round(2.3 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
  {
    id: 'pdf-appraisal',
    name: 'Appraisal.pdf',
    type: 'application/pdf',
    sizeBytes: Math.round(3.25 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
  {
    id: 'doc-memo',
    name: 'Memo.docx',
    type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    sizeBytes: Math.round(7.05 * 1024 * 1024),
    previewUrl: '#',
    downloadUrl: '#',
  },
])

// Build context string for AI summary from row data
const quickSummaryContext = computed<string>(() => {
  const r = props.row || {}
  const parts: string[] = []
  
  const addr = [r.street_address, r.city, r.state, r.zip].filter(Boolean).join(', ')
  if (addr) parts.push(`Address: ${addr}`)
  if (r.current_balance != null) parts.push(`Current Balance: ${r.current_balance}`)
  if (r.total_debt != null) parts.push(`Total Debt: ${r.total_debt}`)
  if (r.seller_as_is != null) parts.push(`Seller As-Is: ${r.seller_as_is}`)
  if (r.seller_arv != null) parts.push(`Seller ARV: ${r.seller_arv}`)
  if (r.asset_status) parts.push(`Asset Status: ${r.asset_status}`)
  if (r.fc_flag) parts.push(`FC Flag: ${r.fc_flag}`)
  if (r.bk_flag) parts.push(`BK Flag: ${r.bk_flag}`)
  
  return parts.join(' | ')
})
</script>

<style scoped>
/* Minimum height with flexbox stretch for equal heights */
.snapshot-card {
  min-height: 350px;
  height: 100%;
}

@media (min-width: 992px) {
  .snapshot-card {
    min-height: 400px;
  }
}
</style>
