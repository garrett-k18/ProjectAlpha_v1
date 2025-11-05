<template>
  <!--
    propertydetails.vue
    - Reusable Property Details card showing address, property attributes, and seller/additional values.
    - Accepts either a full `row` object or, if absent, fetches data by `productId`.
    - Styled per Hyper UI/Bootstrap with acquisitions-consistent header.
  -->
  <div class="card">
    <!-- Header -->
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Property Details</h4>
    </div>

    <!-- Body -->
    <div class="card-body">
      <!-- Empty state -->
      <div v-if="!hasAnyData" class="text-muted text-center py-3">No property details available.</div>

      <!-- Content -->
      <div v-else class="row g-3">
        <!-- Column 1: Core property attributes -->
        <div class="col-md-6">
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
              {{ formatBeds(rowActive?.beds) }} bd / {{ formatBaths(rowActive?.baths) }} ba
            </span>
          </div>

          <div class="mb-2">
            <small class="text-muted d-block">Square Feet</small>
            <span class="fw-semibold text-dark">{{ livingAreaDisplay }}</span>
          </div>

          <div class="mb-2">
            <small class="text-muted d-block">Lot Size</small>
            <span class="fw-semibold text-dark">{{ lotSizeDisplay }}</span>
          </div>

          <div class="mb-2">
            <small class="text-muted d-block">Gross Square Feet</small>
            <span class="fw-semibold text-dark">{{ grossSqFtDisplay }}</span>
          </div>

          <div class="mb-2">
            <small class="text-muted d-block">Units</small>
            <span class="fw-semibold text-dark">{{ unitsDisplay }}</span>
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

        <!-- Column 2: Market & Location descriptors -->
        <div class="col-md-6">
          <div v-for="descriptor in locationDescriptors" :key="descriptor.key" class="mb-2">
            <small class="text-muted d-block">{{ descriptor.label }}</small>
            <span class="fw-semibold text-dark">{{ descriptor.value }}</span>
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
    assetId: { type: [String, Number] as PropType<string | number | null>, default: null },
  },
  setup(props) {
    const fetchedRow = ref<Record<string, any> | null>(null)
    const rowActive = computed(() => props.row ?? fetchedRow.value)

    const blankDisplay = '' // WHAT: Centralized blank display string so property details omit placeholder glyphs when data is unavailable

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
        r.beds != null || r.baths != null || r.sq_ft != null || r.lot_size != null || r.year_built != null ||
        getFirstValue(['msa_name', 'msa', 'metro_area', 'cbsa_name']) ||
        getFirstValue(['county_name', 'county']) ||
        getFirstValue(['neighborhood', 'subdivision', 'area_description']) ||
        getFirstValue(['zoning', 'zoning_class']) ||
        getFirstValue(['flood_zone', 'flood_zone_code']) ||
        getFirstValue(['school_district', 'school_district_name'])
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
      () => props.assetId,
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

    const formatBeds = (v: any): string => {
      if (v == null || v === '') return blankDisplay // WHAT: Provide empty string when bed count missing so snapshot card shows blank per UX request
      const num = Number(v)
      return Number.isFinite(num) ? String(num) : String(v)
    }

    const formatBaths = (v: any): string => {
      if (v == null || v === '') return blankDisplay // WHAT: Mirror bed formatter for bath values while keeping decimals intact when available
      const num = Number(v)
      if (!Number.isFinite(num)) return String(v)
      return num % 1 === 0 ? `${num.toFixed(0)}` : `${num.toFixed(1)}`
    }

    const getFirstValue = (keys: string[]): string => {
      const r = rowActive.value as any
      if (!r) return ''
      for (const key of keys) {
        const value = r?.[key]
        if (value != null && String(value).trim().length > 0) {
          return String(value)
        }
      }
      return ''
    }

    const getNumericValue = (keys: string[]): number | null => {
      const r = rowActive.value as any
      if (!r) return null
      for (const key of keys) {
        const raw = r?.[key]
        if (raw == null || raw === '') continue
        const num = Number(raw)
        if (!Number.isNaN(num)) return num
      }
      return null
    }

    const formatSquareFeet = (value: number | null): string => {
      if (value == null) return blankDisplay
      return `${new Intl.NumberFormat('en-US').format(value)} sq ft`
    }

    const formatUnits = (value: number | null): string => {
      if (value == null) return blankDisplay
      return `${new Intl.NumberFormat('en-US').format(value)}`
    }

    const livingAreaDisplay = computed(() => formatSquareFeet(getNumericValue(['sq_ft', 'living_area_sq_ft', 'gross_living_area', 'gla'])))
    const lotSizeDisplay = computed(() => formatSquareFeet(getNumericValue(['lot_size', 'lot_sqft', 'lot_square_feet', 'land_sq_ft'])))
    const grossSqFtDisplay = computed(() => formatSquareFeet(getNumericValue(['gross_sq_ft', 'building_sq_ft', 'improved_sq_ft'])))
    const unitsDisplay = computed(() => formatUnits(getNumericValue(['units', 'number_of_units', 'unit_count'])))

    const locationDescriptors = computed(() => {
      const descriptorSources: Array<{ key: string; label: string; sample: string; keys: string[] }> = [
        { key: 'msa', label: 'Metropolitan Area', sample: 'Cheyenne Metropolitan Statistical Area', keys: ['msa_name', 'msa', 'metro_area', 'cbsa_name'] },
        { key: 'county', label: 'County', sample: 'Platte County', keys: ['county_name', 'county'] },
        { key: 'neighborhood', label: 'Neighborhood', sample: 'Downtown Wheatland', keys: ['neighborhood', 'subdivision', 'area_description'] },
        { key: 'zoning', label: 'Zoning', sample: 'Residential (R-1)', keys: ['zoning', 'zoning_class'] },
        { key: 'flood', label: 'Flood Zone', sample: 'Zone X (Minimal Risk)', keys: ['flood_zone', 'flood_zone_code'] },
        { key: 'school', label: 'School District', sample: 'Platte County School District #1', keys: ['school_district', 'school_district_name'] },
      ]

      return descriptorSources.map(({ key, label, sample, keys }) => {
        const value = getFirstValue(keys) || sample
        return { key, label, value }
      })
    })

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

    return {
      rowActive,
      hasAnyData,
      fullAddress,
      propertyBadge,
      occupancyBadge,
      blankDisplay,
      formatBeds,
      formatBaths,
      livingAreaDisplay,
      lotSizeDisplay,
      grossSqFtDisplay,
      unitsDisplay,
      locationDescriptors,
    }
  },
})
</script>

<style scoped>
/* No custom styles beyond Hyper/Bootstrap utilities */
</style>
