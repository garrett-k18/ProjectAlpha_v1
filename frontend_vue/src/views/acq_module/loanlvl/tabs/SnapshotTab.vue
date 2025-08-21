<template>
  <!-- Snapshot tab content used inside the product details modal.
       This component intentionally excludes page-level wrappers (Layout, Breadcrumb)
       so it can be embedded within a modal body. -->
  <div class="overflow-hidden">
    <!-- Top summary row with photos and quick facts -->
    <!-- Keep gutters on row; apply horizontal padding on a wrapper to avoid row negative-margin overflow in modal -->
    <div class="px-3 px-lg-4">
      <b-row class="g-3 g-lg-4 align-items-stretch justify-content-center">
      <!-- First column: Photo carousel area, displays images and thumbnails -->
      <b-col lg="4" class="d-flex">
        <!-- Match Hyper UI card look used by Details/Map: white background + subtle shadow -->
        <div class="w-100 h-100">
          <div class="card h-100 d-flex flex-column">
            <div class="card-body d-flex flex-column h-100 overflow-hidden">
              <!-- Reusable global PhotoCarousel component displays product/asset images -->
              <!-- Show carousel only when we have images; otherwise show a small placeholder -->
              <PhotoCarousel
                v-if="imagesToShow.length > 0"
                class="flex-fill h-100"
                :images="imagesToShow"
                :controls="false"
                :indicators="false"
                :loop="true"
                :show-thumbnails="true"
                :interval="0"
                img-class="d-block w-100 h-100"
                :img-max-width="'100%'"
                :img-max-height="'100%'"
                :container-height="carouselHeight"
                :container-max-width="'100%'"
                :thumb-width="thumbWidth"
                :thumb-height="thumbHeight"
              />
              <div v-else class="text-muted text-center py-4 small">Loading photos…</div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Second column: Property details area, shows dynamic details from SellerRawData -->
      <b-col lg="4" class="d-flex">
        <!-- Use the SnapshotDetails component to display property information from the row data -->
        <div class="ps-lg-4 w-100 h-100">
          <!-- Apply h-100 via root-attribute inheritance so the card fills the column height -->
          <SnapshotDetails class="h-100 d-flex flex-column" :row="row" :productId="productId" />
        </div>
      </b-col>
      
      <!-- Third column: Property map to the right of Property details -->
      <b-col lg="4" class="d-flex">
        <div class="ps-lg-4 w-100 h-100">
          <PropertyMap class="h-100 d-flex flex-column" :row="row" :productId="productId" height="100%" />
        </div>
      </b-col>
      </b-row>
    </div>

    <!-- Documents quick view row -->
    <div class="px-3 px-lg-4">
      <b-row class="g-3 g-lg-4 mt-1">
      <b-col lg="3" class="d-flex">
        <div class="w-100 h-100">
          <!-- Reusable global DocumentsQuickView widget; data-agnostic and styled with Hyper UI cards -->
          <DocumentsQuickView
            title="Document Quick View"
            :docs="docItems"
            :maxItems="5"
            :showViewAll="false"
          />
        </div>
      </b-col>
      <!-- Quick AI Summary next to documents list -->
      <b-col lg="9" class="d-flex">
        <div class="ps-lg-4 w-100 h-100">
          <QuickSummary
            class="h-100 d-flex flex-column"
            :context="quickSummaryContext"
            :max-bullets="4"
            :lazy="true"
            title="Asset Highlights"
          />
        </div>
      </b-col>
    </b-row>
    </div>

    <!-- Pricing/stock by outlet table -->
    <div class="px-3 px-lg-4">
      <ValuationMatrix />
    </div>
  </div>
</template>

<script setup lang="ts">
// SnapshotTab.vue
// Purpose: Provide the Snapshot tab content for the acquisitions product details modal.
// Props are designed to be generic so this component remains reusable.

// Import the reusable global PhotoCarousel and its PhotoItem type for strong typing
import PhotoCarousel from '@/1_global/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/1_global/components/PhotoCarousel.vue'
// Import the SnapshotDetails component to display property information
import SnapshotDetails from '@/views/acq_module/loanlvl/components/snapshotdetails.vue'
// Reusable map component to show geocoded address
import PropertyMap from '@/1_global/components/PropertyMap.vue'
// Reusable documents quick view card (data-agnostic)
import DocumentsQuickView from '@/1_global/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/1_global/components/DocumentsQuickView.vue'
// Global AI quick summary card (server-side generated bullets)
import QuickSummary from '@/1_global/components/QuickSummary.vue'
// Modular pricing/stock grid card extracted from inline markup
import ValuationMatrix from '@/views/acq_module/loanlvl/components/valuationMatrix.vue'

// Vue composition API helpers
import { withDefaults, defineProps, ref, computed, watch } from 'vue'
// Centralized Axios instance (baseURL from env; proxied to Django in dev)
import http from '@/lib/http'
// Photos API is public in development; no auth gating required
// Demo documents below are pure metadata; no image thumbnails required

// Strongly-typed props for context
const props = withDefaults(defineProps<{
  // row: optional dataset row for future bindings
  row?: Record<string, any> | null
  // productId: optional identifier for the asset
  productId?: string | number | null
  // Optional sizing overrides for the PhotoCarousel
  // Accept number (pixels) or string (e.g., '100%')
  carouselWidth?: number | string
  carouselHeight?: number | string
  // Optional thumbnail sizing for PhotoCarousel
  thumbWidth?: number | string
  thumbHeight?: number | string
}>(), {
  row: null,
  productId: null,
  // Use fixed dimensions to ensure consistent photo sizing and prevent card resizing
  carouselWidth: 500,
  carouselHeight: 300,
  // Larger, clearer thumbnails by default
  thumbWidth: 120,
  thumbHeight: 90,
})

// Local state: dynamically fetched images from backend
const fetchedImages = ref<PhotoItem[]>([])

// Compute the effective images to display: only fetched photos
const imagesToShow = computed<PhotoItem[]>(() => fetchedImages.value || [])

// Determine which SellerRawData id to load photos for
// Order: productId prop -> row.id -> null
const sourceId = computed<number | null>(() => {
  const idFromProduct = props.productId != null ? Number(props.productId) : null
  const idFromRow = (props.row && props.row.id != null) ? Number(props.row.id) : null
  return idFromProduct ?? idFromRow ?? null
})

// No auth token required for photo fetches (public endpoint in development)

// Fetch photos from backend and normalize into PhotoItem[]
async function loadPhotos(id: number) {
  try {
    // GET /api/acq/photos/<id>/ via baseURL '/api' in dev
    const res = await http.get(`/acq/photos/${id}/`)
    // Response already in { src, alt?, thumb? } format
    const items = (res.data || []) as PhotoItem[]
    fetchedImages.value = items
    // Debug: id and count to help diagnose when demo images still show
    console.debug('[SnapshotTab] loaded photos for', id, 'count:', items.length)
  } catch (err) {
    // Provide actionable logging, but avoid leaking sensitive data
    const status = (err as any)?.response?.status
    if (status === 401) {
      console.warn('[SnapshotTab] 401 Unauthorized fetching photos. Check that an auth token exists and is attached.')
    } else {
      console.warn('Failed to load photos for id', id, err)
    }
    fetchedImages.value = []
  }
}

// Load immediately when id is available and whenever it changes
watch(sourceId, (id) => {
  if (id && !Number.isNaN(id)) {
    loadPhotos(id)
  } else {
    fetchedImages.value = []
  }
}, { immediate: true })

// Debug: observe when row data is supplied so we can verify full-page fetch vs modal-provided props
watch(() => props.row, (r) => {
  // eslint-disable-next-line no-console
  console.debug('[SnapshotTab] row updated:', r ? Object.keys(r) : null)
}, { immediate: true })

// No token watcher needed since photos endpoint is public in development

// -----------------------------------------------------------------------------
// Documents quick view data (placeholder)
// -----------------------------------------------------------------------------
// This widget is data-agnostic. Until a backend endpoint is wired, we expose a
// computed array that parents can override in the future. Keeping it empty will
// show the component's empty state.
const docItems = computed<DocumentItem[]>(() => {
  // Demo items renamed per request
  return [
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
  ]
})

// Build a concise context string for the AI summary from available row fields
// Keep this defensively coded so modal usage without row data does not break
const quickSummaryContext = computed<string>(() => {
  const r = props.row || {}
  const parts: string[] = []
  // Address
  const addr = [r.street_address, r.city, r.state, r.zip].filter(Boolean).join(', ')
  if (addr) parts.push(`Address: ${addr}`)
  // Financials
  if (r.current_balance != null) parts.push(`Current Balance: ${r.current_balance}`)
  if (r.total_debt != null) parts.push(`Total Debt: ${r.total_debt}`)
  if (r.seller_as_is != null) parts.push(`Seller As-Is: ${r.seller_as_is}`)
  if (r.seller_arv != null) parts.push(`Seller ARV: ${r.seller_arv}`)
  // Categorical flags
  if (r.asset_status) parts.push(`Asset Status: ${r.asset_status}`)
  if (r.fc_flag) parts.push(`FC Flag: ${r.fc_flag}`)
  if (r.bk_flag) parts.push(`BK Flag: ${r.bk_flag}`)
  // Join into a short paragraph for summarization
  return parts.join(' | ')
})
</script>
