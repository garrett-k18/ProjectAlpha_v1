<template>
  <!-- Root padding container keeps spacing consistent with modal body -->
  <div class="px-3 px-lg-4">
    <!-- Three-card layout for snapshot summary content -->
    <b-row class="g-3 align-items-stretch" style="min-height: 400px;">
      <b-col lg="4" class="d-flex">
        <AssetSummary
          class="h-100 w-100"
          :row="row"
          :assetHubId="assetHubId"
        />
      </b-col>

      <b-col lg="4" class="d-flex">
        <div class="card h-100 w-100">
          <div class="card-body p-0 d-flex flex-column h-100">
            <div class="flex-fill d-flex">
              <PhotoCarousel
                v-if="imagesToShow.length > 0"
                class="w-100"
                :images="imagesToShow"
                :interval="0"
                :loop="true"
                :force-show-controls="true"
                :force-show-thumbnails="true"
                :show-thumbnails="true"
                :thumb-width="thumbWidth"
                :thumb-height="thumbHeight"
                :bg-transparent="true"
              />
              <div v-else class="w-100 d-flex align-items-center justify-content-center text-muted small">
                No Photos Available
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <b-col lg="4" class="d-flex">
        <div class="card h-100 w-100">
          <div class="card-body p-0 h-100">
            <PropertyMap
              class="w-100 h-100"
              :row="row"
              :assetHubId="assetHubId"
              :height="'100%'"
              :bare="true"
              :zoom="15"
              :showMarker="true"
            />
          </div>
        </div>
      </b-col>
    </b-row>
  </div>
</template>

<script setup lang="ts">
import { computed, withDefaults, defineProps } from 'vue' // Import Vue helpers for typed props and derived state
import PropertyMap from '@/components/PropertyMap.vue' // Import shared map component to display asset location
import PhotoCarousel from '@/components/PhotoCarousel.vue' // Import shared photo carousel component for asset imagery
import type { PhotoItem } from '@/components/PhotoCarousel.vue' // Import PhotoItem type for strong typing of carousel data
import AssetSummary from '@/views/am_module/loanlvl/components/asset_summary.vue' // Import the Asset Summary card component for Snapshot tab use

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null // Optional row payload containing snapshot fields
  assetHubId?: string | number | null // Optional asset hub identifier for downstream components
  carouselWidth?: number | string // Legacy width prop retained for compatibility with acquisitions props
  carouselHeight?: number | string // Legacy height prop retained for compatibility with acquisitions props
  thumbWidth?: number | string // Optional thumbnail width passed through to carousel
  thumbHeight?: number | string // Optional thumbnail height passed through to carousel
}>(), {
  row: null, // Default row to null to keep computed fields defensive
  assetHubId: null, // Default asset ID to null for parity with other tabs
  carouselWidth: 500, // Maintain historical default width for carousel consumers
  carouselHeight: 280, // Maintain historical default height for carousel consumers
  thumbWidth: 120, // Default thumbnail width to match acquisitions layout
  thumbHeight: 90, // Default thumbnail height to match acquisitions layout
})

const dash = '—' // Define fallback glyph for missing values

const maybeNumber = (value: unknown): number | null => {
  if (value === null || value === undefined) {
    return null
  }
  const asNumber = Number(value)
  return Number.isFinite(asNumber) ? asNumber : null
} // Helper that safely parses numeric values

const formatCurrency = (value: unknown): string => {
  const numericValue = maybeNumber(value)
  if (numericValue === null) {
    return dash
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(numericValue)
} // Helper that renders numbers as USD currency without decimals

const formatPercent = (value: unknown): string => {
  const numericValue = maybeNumber(value)
  if (numericValue === null) {
    return dash
  }
  const percentValue = Math.abs(numericValue) <= 1 ? numericValue * 100 : numericValue
  return `${percentValue.toFixed(2)}%`
} // Helper that renders either decimal or whole-number percent values

const formatString = (value: unknown): string => {
  if (value === null || value === undefined || value === '') {
    return dash
  }
  return String(value)
} // Helper that coerces values to strings or dash fallback

const imagesToShow = computed<PhotoItem[]>(() => {
  const photos = props.row?.photos as PhotoItem[] | undefined
  if (Array.isArray(photos) && photos.length > 0) {
    return photos
  }
  return []
}) // Computed list of photos available for the carousel

const thumbWidth = computed<number | string>(() => props.thumbWidth) // Computed passthrough for carousel thumbnail width

const thumbHeight = computed<number | string>(() => props.thumbHeight) // Computed passthrough for carousel thumbnail height
</script>
