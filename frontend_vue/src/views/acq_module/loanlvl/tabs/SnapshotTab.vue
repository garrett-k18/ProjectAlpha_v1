<template>
  <!-- Snapshot tab content used inside the product details modal.
       This component intentionally excludes page-level wrappers (Layout, Breadcrumb)
       so it can be embedded within a modal body. -->
  <div>
    <!-- Top summary row with photos and quick facts -->
    <!-- Use responsive gutters for better spacing; keep padding so content doesn't touch edges -->
    <!-- Center the two primary columns horizontally; rely on Bootstrap utilities per docs -->
    <b-row class="g-3 g-lg-4 px-3 px-lg-4 align-items-stretch justify-content-center">
      <!-- First column: Photo carousel area, displays images and thumbnails -->
      <b-col lg="4" class="d-flex">
        <!-- Match Hyper UI card look used by Details/Map: white background + subtle shadow -->
        <div class="w-100 h-100">
          <div class="card h-100 d-flex flex-column">
            <div class="card-body d-flex flex-column justify-content-center">
              <!-- Reusable global PhotoCarousel component displays product/asset images -->
              <!-- Show carousel only when we have images; otherwise show a small placeholder -->
              <PhotoCarousel
                v-if="imagesToShow.length > 0"
                :images="imagesToShow"
                :controls="false"
                :indicators="false"
                :loop="true"
                :show-thumbnails="true"
                :interval="0"
                img-class="d-block mx-auto w-100"
                :img-max-width="carouselWidth"
                :img-max-height="carouselHeight"
                :container-max-width="carouselWidth"
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

    <!-- Pricing/stock by outlet table -->
    <div class="table-responsive mt-4">
      <table class="table table-bordered table-centered mb-0">
        <thead class="table-light">
          <tr>
            <th>Outlets</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Revenue</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>ASOS Ridley Outlet - NYC</td>
            <td>$139.58</td>
            <td>
              <div class="progress-w-percent mb-0">
                <span class="progress-value">478 </span>
                <div class="progress progress-sm">
                  <div class="progress-bar bg-success" role="progressbar" style="width: 56%;" aria-valuenow="56" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
              </div>
            </td>
            <td>$1,89,547</td>
          </tr>
          <tr>
            <td>Marco Outlet - SRT</td>
            <td>$149.99</td>
            <td>
              <div class="progress-w-percent mb-0">
                <span class="progress-value">73 </span>
                <div class="progress progress-sm">
                  <div class="progress-bar bg-danger" role="progressbar" style="width: 16%;" aria-valuenow="16" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
              </div>
            </td>
            <td>$87,245</td>
          </tr>
          <tr>
            <td>Chairtest Outlet - HY</td>
            <td>$135.87</td>
            <td>
              <div class="progress-w-percent mb-0">
                <span class="progress-value">781 </span>
                <div class="progress progress-sm">
                  <div class="progress-bar bg-success" role="progressbar" style="width: 72%;" aria-valuenow="72" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
              </div>
            </td>
            <td>$5,87,478</td>
          </tr>
          <tr>
            <td>Nworld Group - India</td>
            <td>$159.89</td>
            <td>
              <div class="progress-w-percent mb-0">
                <span class="progress-value">815 </span>
                <div class="progress progress-sm">
                  <div class="progress-bar bg-success" role="progressbar" style="width: 89%;" aria-valuenow="89" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
              </div>
            </td>
            <td>$55,781</td>
          </tr>
        </tbody>
      </table>
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

// Vue composition API helpers
import { withDefaults, defineProps, ref, computed, watch } from 'vue'
// Centralized Axios instance (baseURL from env; proxied to Django in dev)
import http from '@/lib/http'
// Photos API is public in development; no auth gating required

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
</script>
