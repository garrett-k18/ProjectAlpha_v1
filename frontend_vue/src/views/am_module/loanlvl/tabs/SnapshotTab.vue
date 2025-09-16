<template>
  <!-- AM Snapshot: Photos + Valuation + Documents quick view -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <!-- Left: Photo carousel within a card -->
    <b-col lg="8" class="d-flex">
      <div class="card w-100 h-100 d-flex flex-column">
        <div class="d-flex card-header justify-content-between align-items-center">
          <h4 class="header-title mb-0">Photos</h4>
        </div>
        <div class="card-body pt-2">
          <PhotoCarousel
            :items="images"
            :width="carouselWidth"
            :height="carouselHeight"
            :thumbWidth="thumbWidth"
            :thumbHeight="thumbHeight"
          />
        </div>
      </div>
    </b-col>

    <!-- Right: Property map (reuse global component) -->
    <b-col lg="4" class="d-flex">
      <div class="w-100 h-100">
        <PropertyMap class="w-100 h-100 d-flex flex-column" :row="row" :productId="productId" height="100%" />
      </div>
    </b-col>
  </b-row>

  <!-- Valuation + Documents row -->
  <b-row class="g-3 mt-1 align-items-stretch px-3 px-lg-4">
    <b-col lg="9" class="d-flex">
      <div class="w-100 h-100">
        <ValuationMatrix class="h-100 d-flex flex-column" :row="row" :productId="productId" />
      </div>
    </b-col>

    <b-col lg="3" class="d-flex">
      <div class="w-100 h-100">
        <DocumentsQuickView title="Document Quick View" :docs="docItems" :maxItems="5" :showViewAll="false" />
      </div>
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, watch } from 'vue'
import http from '@/lib/http'
import PropertyMap from '@/components/PropertyMap.vue'
import PhotoCarousel from '@/components/PhotoCarousel.vue'
import DocumentsQuickView from '@/components/DocumentsQuickView.vue'
import type { DocumentItem } from '@/components/DocumentsQuickView.vue'

export type PhotoItem = { src: string; alt?: string; thumb?: string; type?: string }

const fetchedImages = ref<PhotoItem[]>([])
const images = computed<PhotoItem[]>(() => fetchedImages.value)

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
  carouselWidth?: number | string
  carouselHeight?: number | string
  thumbWidth?: number | string
  thumbHeight?: number | string
}>(), {
  row: null,
  productId: null,
  carouselWidth: 500,
  carouselHeight: 300,
  thumbWidth: 120,
  thumbHeight: 90,
})

const sourceId = computed<number | null>(() => {
  // Prefer explicit productId, fallback to row.id
  const idFromProduct = props.productId != null ? Number(props.productId) : null
  const idFromRow = (props.row && props.row.id != null) ? Number(props.row.id) : null
  return idFromProduct ?? idFromRow ?? null
})

async function loadPhotos(id: number) {
  try {
    const res = await http.get(`/am/assets/${id}/photos/`)
    fetchedImages.value = (res.data || []) as PhotoItem[]
    console.debug('[AM SnapshotTab] loaded photos for', id, 'count:', fetchedImages.value.length)
  } catch (err) {
    console.warn('[AM SnapshotTab] failed to load photos for id', id, err)
    fetchedImages.value = []
  }
}

watch(sourceId, (id) => {
  if (id && !Number.isNaN(id)) {
    loadPhotos(id)
  } else {
    fetchedImages.value = []
  }
}, { immediate: true })

// Demo docs (metadata only)
const docItems = computed<DocumentItem[]>(() => [
  { id: 'pdf-bpo', name: 'BPO.pdf', type: 'application/pdf', sizeBytes: Math.round(2.3 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
  { id: 'pdf-appraisal', name: 'Appraisal.pdf', type: 'application/pdf', sizeBytes: Math.round(3.25 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
  { id: 'doc-memo', name: 'Memo.docx', type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', sizeBytes: Math.round(7.05 * 1024 * 1024), previewUrl: '#', downloadUrl: '#' },
])
</script>
