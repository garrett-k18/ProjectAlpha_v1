<template>
  <div>
    <div class="row g-3 align-items-stretch">
      <!-- Left: Photo carousel -->
      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <div class="card h-100 d-flex flex-column w-100">
          <div class="card-body pt-0 d-flex flex-column h-100 overflow-hidden">
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

      <!-- Middle: Property Details card -->
      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <PropertyDetails :row="row" :productId="productId" class="h-100 d-flex flex-column w-100" />
      </div>

      <!-- Right: Property Map -->
      <div class="col-12 col-lg-6 col-xl-4 d-flex">
        <div class="card h-100 d-flex flex-column w-100">
          <div class="card-body pt-0 d-flex flex-column h-100 p-0">
            <PropertyMap class="h-100 d-flex flex-column" :row="row" :productId="productId" height="100%" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, computed, watch } from 'vue'
import PropertyDetails from '@/views/acq_module/loanlvl/components/propertydetails.vue'
import PhotoCarousel from '@/1_global/components/PhotoCarousel.vue'
import type { PhotoItem } from '@/1_global/components/PhotoCarousel.vue'
import PropertyMap from '@/1_global/components/PropertyMap.vue'
import http from '@/lib/http'

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

// Photo loading logic mirrors SnapshotTab for consistency
const fetchedImages = ref<PhotoItem[]>([])
const imagesToShow = computed<PhotoItem[]>(() => fetchedImages.value || [])

const sourceId = computed<number | null>(() => {
  const idFromProduct = props.productId != null ? Number(props.productId) : null
  const idFromRow = (props.row && (props.row as any).id != null) ? Number((props.row as any).id) : null
  return idFromProduct ?? idFromRow ?? null
})

async function loadPhotos(id: number) {
  try {
    const res = await http.get(`/acq/photos/${id}/`)
    fetchedImages.value = (res.data || []) as PhotoItem[]
    console.debug('[PropertyDetailsTab] loaded photos for', id, 'count:', fetchedImages.value.length)
  } catch (err) {
    console.warn('[PropertyDetailsTab] failed to load photos for', id, err)
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
</script>
