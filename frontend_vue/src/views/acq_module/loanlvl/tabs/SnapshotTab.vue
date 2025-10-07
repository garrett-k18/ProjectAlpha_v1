<template>
  <!-- Snapshot tab content used inside the product details modal.
       This component intentionally excludes page-level wrappers (Layout, Breadcrumb)
       so it can be embedded within a modal body. -->
  <div class="px-3 px-lg-3">
    <LoanlvlWidgets :row="row" class="mb-2" />
    <!-- Top summary row with photos and quick facts -->
    <b-row class="g-3 align-items-stretch">
      <!-- Left column: Asset Highlights (QuickSummary) -->
      <b-col lg="4" class="d-flex">
        <div class="w-100" style="height: 380px;">
          <QuickSummary
            class="w-100 h-100 d-flex flex-column"
            :context="quickSummaryContext"
            :max-bullets="4"
            :lazy="true"
            title="Asset Summary"
          />
        </div>
      </b-col>

      <!-- Middle column: Photo carousel area, displays images and thumbnails -->
      <b-col lg="4" class="d-flex">
        <!-- Match Hyper UI card look used by Details/Map: white background + subtle shadow -->
        <div class="w-100" style="height: 380px;">
          <div class="card w-100 h-100 d-flex flex-column">
            <div class="card-body pt-0 pb-0 d-flex flex-column h-100">
              <!-- Reusable global PhotoCarousel component displays product/asset images -->
              <!-- Show carousel only when we have images; otherwise show a small placeholder -->
              <PhotoCarousel
                v-if="imagesToShow.length > 0"
                class="flex-fill h-100"
                :images="imagesToShow"
                :force-show-controls="true"
                :force-show-thumbnails="true"
                :loop="true"
                :show-thumbnails="true"
                :interval="0"
                img-class="d-block w-100 h-100"
                :img-max-width="'85%'"
                :img-max-height="'100%'"
                :container-height="carouselContainerHeight"
                :container-max-width="'100%'"
                :thumb-width="90"
                :thumb-height="54"
                :square="true"
              />
              <div v-else class="flex-fill d-flex align-items-center justify-content-center text-muted small">No Photos</div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Right column: Property map -->
      <b-col lg="4" class="d-flex">
        <div class="w-100" style="height: 380px;">
          <PropertyMap 
            class="w-100 h-100 d-flex flex-column" 
            :row="row" 
            :assetHubId="assetId" 
            :height="380"
            :zoom="15"
            :showMarker="true"
          />
        </div>
      </b-col>
      </b-row>
    <!-- Documents + Valuation + Summary row (match standard gutters). Place Valuation left of Documents. -->
    <!-- Standard gutters to match other tabs -->
    <b-row class="g-3 mt-1 align-items-stretch">
        <!-- Valuation Matrix (component renders its own card now) -->
        <b-col lg="9" class="d-flex">
          <div class="w-100 h-100">
            <ValuationMatrix class="h-100 d-flex flex-column" :row="row" :assetId="assetId" :module="module" />
          </div>
        </b-col>

        <!-- Documents quick view card (right) -->
        <b-col lg="3" class="d-flex">
          <div class="w-100 h-100">
            <DocumentsQuickView
              title="Document Quick View"
              :docs="docItems"
              :maxItems="5"
              :showViewAll="false"
            />
          </div>
        </b-col>
      </b-row>
    </div>
</template>

<script setup lang="ts">
// SnapshotTab.vue
// Purpose: Provide the Snapshot tab content for the acquisitions product details modal.
// Props are designed to be generic so this component remains reusable.

// Import the reusable global PhotoCarousel and its PhotoItem type for strong typing
import PhotoCarousel from '@/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/components/PhotoCarousel.vue'
// Import the SnapshotDetails component to display property information
// Reusable map component to show geocoded address
import PropertyMap from '@/components/PropertyMap.vue'
// Reusable documents quick view card (data-agnostic)
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'
// Global AI quick summary card (server-side generated bullets)
import QuickSummary from '@/components/QuickSummary.vue'
// Modular pricing/stock grid card extracted from inline markup
import ValuationMatrix from '@/views/acq_module/loanlvl/components/valuationMatrix.vue'
// Hyper UI widget: simple stat with icon
import LoanlvlWidgets from '@/components/widgets/loanlvl-widgets.vue'

// Vue composition API helpers
import { withDefaults, defineProps, ref, computed, watch } from 'vue'
// Centralized Axios instance (baseURL from env; proxied to Django in dev)
import http from '@/lib/http'
// Photos API is public in development; no auth gating required

// Strongly-typed props for context
const props = withDefaults(defineProps<{
  // row: optional dataset row for future bindings
  row?: Record<string, any> | null
  // assetId: Asset Hub ID for the current asset
  assetId?: string | number | null
  // module: selects API base ('acq' | 'am'); defaults to acquisitions
  module?: 'acq' | 'am'
  // Optional sizing overrides for the PhotoCarousel
  carouselWidth?: number | string
  carouselHeight?: number | string
  thumbWidth?: number | string
  thumbHeight?: number | string
  // Optional override for the valuation matrix
  valuationMatrixWidth?: number | string
}>(), {
  row: null,
  assetId: null,
  module: 'acq',
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

// Reserve space for thumbnails when there are multiple images so arrows and
// thumbs are not clipped by the parent overflow. Use a calc() string so it
// adapts to the parent container height.
const carouselContainerHeight = computed<string>(() => {
  // Reserve space for thumbnails even when only one image is available
  const hasThumbs = imagesToShow.value.length >= 1
  // Parse numeric thumb height if provided as a number or string with px
  const parsePx = (v: number | string | undefined, fallback: number): number => {
    if (typeof v === 'number' && Number.isFinite(v)) return v
    if (typeof v === 'string') {
      const m = v.match(/(\d+)(?=px)?/)
      if (m) return Number(m[1])
    }
    return fallback
  }
  const thumbH = parsePx((props as any).thumbHeight, 60)
  const gutter = 8
  return hasThumbs ? `calc(100% - ${thumbH + gutter}px)` : '100%'
})

// Determine which SellerRawData id to load photos for
// Order: assetId prop -> row.id -> null
const sourceId = computed<number | null>(() => {
  const idFromProduct = props.assetId != null ? Number(props.assetId) : null
  const idFromRow = (props.row && props.row.id != null) ? Number(props.row.id) : null
  const result = idFromProduct ?? idFromRow ?? null
  console.log('[SnapshotTab] assetId=', props.assetId, 'row.id=', (props.row as any)?.id, 'using=', result)
  return result
})

// No auth token required for photo fetches (public endpoint in development)

// Fetch photos from backend and normalize into PhotoItem[]
async function loadPhotos(id: number) {
  try {
    // Choose endpoint based on module: AM uses boarded asset photos; ACQ uses SellerRawData photos
    const url = (props as any).module === 'am' ? `/am/assets/${id}/photos/` : `/acq/photos/${id}/`
    const res = await http.get(url)
    // Response already in { src, alt?, thumb? } format
    const items = (res.data || []) as PhotoItem[]
    fetchedImages.value = items
    // Debug: id and count to help diagnose when demo images still show
    console.debug('[SnapshotTab] loaded photos for', id, 'module=', (props as any).module, 'count:', items.length)
  } catch (err) {
    // Provide actionable logging, but avoid leaking sensitive data
    const status = (err as any)?.response?.status
    if (status === 401) {
      console.warn('[SnapshotTab] 401 Unauthorized fetching photos. Check that an auth token exists and is attached.')
    } else {
      console.warn('Failed to load photos for id', id, 'module=', (props as any).module, err)
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
