<template>
  <!--
    propertydetails.vue
    - Reusable Property Details card showing address, property attributes, and seller/additional values.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Styled per Hyper UI/Bootstrap with acquisitions-consistent header.
  -->
  <div class="card h-100">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Property Details</h4>
    </div>

    <!-- Body -->
    <div class="card-body pt-0">
      <!-- Empty state -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">No property details available.</div>

      <!-- Content -->
      <div v-else class="row g-3">
        <!-- Column: Address + Type/Occupancy and core attributes -->
        <div class="col-12">
          <div v-if="fullAddress" class="mb-2">
            <small class="text-muted d-block">Address</small>
            <span class="fw-semibold text-dark">{{ fullAddress }}</span>
          </div>

          <div v-if="rowActive?.property_type" class="mb-2">
            <small class="text-muted d-block">Property Type</small>
            <span
              v-if="propertyBadge"
              class="badge rounded-pill px-3 py-1 fs-6 fw-semibold"
              :class="propertyBadge.color"
              :title="propertyBadge.title || propertyBadge.label"
            >
              {{ propertyBadge.label }}
            </span>
            <span v-else class="fw-semibold text-dark">{{ rowActive?.property_type }}</span>
          </div>

          <div v-if="rowActive?.beds !== null || rowActive?.baths !== null" class="mb-2">
            <small class="text-muted d-block">Bed / Bath</small>
            <span class="fw-semibold text-dark">
              {{ rowActive?.beds || 'N/A' }} bd / {{ rowActive?.baths ? rowActive.baths.toFixed(1) : 'N/A' }} ba
            </span>
          </div>

          <div v-if="rowActive?.sq_ft" class="mb-2">
            <small class="text-muted d-block">Square Feet</small>
            <span class="fw-semibold text-dark">
              {{ new Intl.NumberFormat().format(rowActive.sq_ft) }} sq ft
            </span>
          </div>

          <div v-if="rowActive?.lot_size" class="mb-2">
            <small class="text-muted d-block">Lot Size</small>
            <span class="fw-semibold text-dark">
              {{ new Intl.NumberFormat().format(rowActive.lot_size) }} sq ft
            </span>
          </div>

          <div v-if="rowActive?.year_built" class="mb-2">
            <small class="text-muted d-block">Year Built</small>
            <span class="fw-semibold text-dark">{{ rowActive.year_built }}</span>
          </div>

          <div v-if="rowActive?.occupancy" class="mb-2">
            <small class="text-muted d-block">Occupancy</small>
            <span
              v-if="occupancyBadge"
              class="badge rounded-pill px-3 py-1 fs-6 fw-semibold"
              :class="occupancyBadge.color"
              :title="occupancyBadge.title || occupancyBadge.label"
            >
              {{ occupancyBadge.label }}
            </span>
            <span v-else class="fw-semibold text-dark">{{ rowActive?.occupancy }}</span>
          </div>
        </div>

        <!-- Removed seller/additional valuation fields per request -->
      </div>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * propertydetails.vue
 * - Displays address (street, city, state, zip), property_type, occupancy,
 *   and seller/additional values and dates.
 * - Props allow passing a `row` directly or fetching by `productId`.
 */
import { defineComponent, computed, ref, watch } from 'vue'
import type { PropType } from 'vue'
import http from '@/lib/http'

export default defineComponent({
  name: 'PropertyDetails',
  props: {
    row: { type: Object as PropType<Record<string, any> | null>, default: null },
    productId: { type: [String, Number] as PropType<string | number | null>, default: null },
  },
  setup(props) {
    const fetchedRow = ref<Record<string, any> | null>(null)
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    const fullAddress = computed(() => {
      const r = rowActive.value as any
      if (!r) return ''
      const parts = [r.street_address, r.city, r.state, r.zip].filter(Boolean)
      return parts.join(', ')
    })

    const hasAnyData = computed<boolean>(() => {
      const r = rowActive.value as any
      return !!(r && (
        r.street_address || r.city || r.state || r.zip ||
        r.property_type || r.occupancy ||
        r.beds != null || r.baths != null || r.sq_ft != null || r.lot_size != null || r.year_built != null
      ))
    })

    async function loadRowById(id: number) {
      try {
        const res = await http.get(`/acq/raw-data/by-id/${id}/`)
        fetchedRow.value = res.data && Object.keys(res.data).length ? res.data : null
        // eslint-disable-next-line no-console
        console.debug('[PropertyDetails] loaded row for', id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('[PropertyDetails] failed to load row for', id, err)
        fetchedRow.value = null
      }
    }

    watch(
      () => props.productId,
      (raw) => {
        const id = raw != null ? Number(raw) : NaN
        if (!props.row && Number.isFinite(id)) {
          loadRowById(id)
        } else if (!Number.isFinite(id)) {
          fetchedRow.value = null
        }
      },
      { immediate: true }
    )

    const formatCurrency = (v: any) => {
      if (v != null && !isNaN(v)) {
        return new Intl.NumberFormat('en-US', { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(Number(v))
      }
      return 'N/A'
    }

    const formatDate = (v: any) => (v ? new Date(v).toLocaleDateString('en-US') : 'N/A')

    // Badge color maps copied from AG Grid configuration to keep visual parity
    // Property Type badge colors
    const propertyTypeBadgeMap: Record<string, { label: string; color: string; title?: string }> = {
      'SFR': { label: 'SFR', color: 'bg-success', title: 'Single Family Residence' },
      'Manufactured': { label: 'Manufactured', color: 'bg-info', title: 'Manufactured Home' },
      'Condo': { label: 'Condo', color: 'bg-primary', title: 'Condominium' },
      '2-4 Family': { label: '2-4 Family', color: 'bg-warning', title: '2-4 Family Property' },
      'Land': { label: 'Land', color: 'bg-danger', title: 'Vacant Land' },
      'Multifamily 5+': { label: 'Multifamily 5+', color: 'bg-secondary', title: 'Multifamily 5+ Units' },
    }

    // Occupancy badge colors
    const occupancyBadgeMap: Record<string, { label: string; color: string; title?: string }> = {
      'Vacant': { label: 'Vacant', color: 'bg-danger', title: 'Property is Vacant' },
      'Occupied': { label: 'Occupied', color: 'bg-success', title: 'Property is Occupied' },
      'Unknown': { label: 'Unknown', color: 'bg-warning', title: 'Occupancy Status Unknown' },
    }

    // Compute badges from current row
    const propertyBadge = computed(() => {
      const r = rowActive.value as any
      if (!r || !r.property_type) return null
      const key = String(r.property_type)
      return propertyTypeBadgeMap[key] || null
    })

    const occupancyBadge = computed(() => {
      const r = rowActive.value as any
      if (!r || !r.occupancy) return null
      const key = String(r.occupancy)
      return occupancyBadgeMap[key] || null
    })

    return { rowActive, hasAnyData, fullAddress, formatCurrency, formatDate, propertyBadge, occupancyBadge }
  },
})
</script>

<style scoped>
/* No custom styles beyond Hyper/Bootstrap utilities */
</style>
