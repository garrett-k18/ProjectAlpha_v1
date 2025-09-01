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
        <!-- Column 1: Address + Type/Occupancy -->
        <div class="col-md-6">
          <div v-if="fullAddress" class="mb-2">
            <small class="text-muted d-block">Address</small>
            <span class="fw-semibold text-dark">{{ fullAddress }}</span>
          </div>

          <div v-if="rowActive?.property_type" class="mb-2">
            <small class="text-muted d-block">Property Type</small>
            <span class="fw-semibold text-dark">{{ rowActive?.property_type }}</span>
          </div>

          <div v-if="rowActive?.occupancy" class="mb-2">
            <small class="text-muted d-block">Occupancy</small>
            <span class="fw-semibold text-dark">{{ rowActive?.occupancy }}</span>
          </div>
        </div>

        <!-- Column 2: Seller/Additional Values -->
        <div class="col-md-6">
          <div v-if="rowActive?.seller_value_date" class="mb-2">
            <small class="text-muted d-block">Seller Value Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.seller_value_date) }}</span>
          </div>

          <div v-if="rowActive?.seller_arv_value != null" class="mb-2">
            <small class="text-muted d-block">Seller ARV Value</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.seller_arv_value) }}</span>
          </div>

          <div v-if="rowActive?.seller_asis_value != null" class="mb-2">
            <small class="text-muted d-block">Seller As-Is Value</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.seller_asis_value) }}</span>
          </div>

          <div v-if="rowActive?.additional_asis_value != null" class="mb-2">
            <small class="text-muted d-block">Additional As-Is Value</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.additional_asis_value) }}</span>
          </div>

          <div v-if="rowActive?.additional_arv_value != null" class="mb-2">
            <small class="text-muted d-block">Additional ARV Value</small>
            <span class="fw-semibold text-dark">{{ formatCurrency(rowActive?.additional_arv_value) }}</span>
          </div>

          <div v-if="rowActive?.additional_value_date" class="mb-2">
            <small class="text-muted d-block">Additional Value Date</small>
            <span class="fw-semibold text-dark">{{ formatDate(rowActive?.additional_value_date) }}</span>
          </div>
        </div>
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
        r.street_address || r.city || r.state || r.zip || r.property_type || r.occupancy ||
        r.seller_value_date || r.seller_arv_value != null || r.seller_asis_value != null ||
        r.additional_asis_value != null || r.additional_arv_value != null || r.additional_value_date
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

    return { rowActive, hasAnyData, fullAddress, formatCurrency, formatDate }
  },
})
</script>

<style scoped>
/* No custom styles beyond Hyper/Bootstrap utilities */
</style>
