<template>
  <div class="card flex-grow-1 w-100">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Dispersion</h4>
      <!-- Filter dropdown for asset master status -->
      <div class="d-flex align-items-center gap-2">
        <label for="assetStatusFilter" class="small mb-0">Filter</label>
        <select 
          id="assetStatusFilter" 
          class="form-select form-select-sm" 
          v-model="selectedStatus" 
          @change="onStatusFilterChange"
          style="width: auto;"
        >
          <option value="">All</option>
          <option value="ACTIVE">Active</option>
          <option value="LIQUIDATED">Liquidated</option>
        </select>
      </div>
    </div>

    <div class="card-body py-0 d-flex flex-column">
      <div class="row flex-grow-1">
        <!-- WHAT: Left column – compact state summary bands stacked vertically, centered vertically within the card. -->
        <div
          v-if="markerSummaries.length > 0"
          class="col-12 col-lg-3 order-2 order-lg-1 mb-3 mb-lg-0 d-flex flex-column justify-content-center"
        >
          <div class="mb-2">
            <span class="text-muted text-uppercase small fw-semibold">Top States</span>
          </div>

          <div
            v-for="summary in markerSummaries"
            :key="summary.id"
            class="mb-2"
          >
            <div class="d-flex align-items-center gap-2">
              <span class="text-muted small" style="min-width: 2.5rem;">{{ summary.label }}</span>
              <div class="progress progress-sm flex-grow-1 mb-0">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="`width: ${summary.progressPercent}%;`"
                  :aria-valuenow="summary.count"
                  aria-valuemin="0"
                  :aria-valuemax="summary.maxCount"
                ></div>
              </div>
              <span class="progress-value fw-bold text-nowrap small">{{ summary.count }} assets</span>
            </div>
          </div>
        </div>

        <!-- WHAT: Right column – give the US map majority of the horizontal space. -->
        <div class="col-12 col-lg-9 order-1 order-lg-2 d-flex align-items-center justify-content-center">
          <div class="w-100">
            <!-- WHAT: Render jsVectorMap via wrapper with backend-driven markers filtered by asset master status. -->
            <VectorMap 
              id="am-dispersion-map" 
              :map-height="380" 
              :location-data="mapMarkers"
              :marker-color="'#727cf5'"
              @marker-click="handleMarkerClick"
            />
          </div>

          <!-- WHAT: Display graceful fallback when zero markers are returned (e.g., filters exclude all assets). -->
          <div v-if="markerSummaries.length === 0" class="py-3 text-center text-muted">
            No active assets found for the current filters.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted, ref } from 'vue'; // WHAT: Vue APIs for component definition, derived state, and lifecycle hooks.
import VectorMap from "./vectorMap.vue"; // WHAT: Local wrapper around jsVectorMap for US projection rendering.
import { useAssetDispersionStore } from '@/stores/assetDispersion'; // WHAT: Pinia store supplying backend-driven dispersion markers.

export default defineComponent({
  name: 'AssetDispersion', // WHAT: Component identifier updated to match file rename for clearer Vue devtools labeling.
  components: { VectorMap }, // WHAT: Register child components required by the template.
  setup(_, { emit }) {
    const dispersionStore = useAssetDispersionStore(); // WHAT: Instantiate the Pinia store to access markers/actions.
    const selectedStatus = ref<string>(''); // WHAT: Reactive state for asset master status filter (empty = All, ACTIVE, LIQUIDATED)

    const mapMarkers = computed(() => dispersionStore.vectorMarkers); // WHAT: Derive jsVectorMap-ready markers from the store.
    const rawMarkers = computed(() => dispersionStore.markers); // WHAT: Access raw backend payload for density summaries.

    const markerSummaries = computed(() => {
      const markersArray = Array.isArray(rawMarkers.value) ? rawMarkers.value : []; // WHAT: Ensure safe array iteration over store payload.
      const aggregates = new Map<string, { count: number; stateLabel: string }>(); // WHAT: Accumulate counts keyed by normalized state abbreviation.

      markersArray.forEach((marker) => {
        const normalizedState = typeof marker.state === 'string' && marker.state.trim().length > 0 ? marker.state.trim().toUpperCase() : 'UNKNOWN'; // WHAT: Normalize to uppercase or fallback when missing.
        const current = aggregates.get(normalizedState) ?? { count: 0, stateLabel: normalizedState };
        current.count += Number(marker.count ?? 1); // WHAT: Increment count per asset observed for the state.
        aggregates.set(normalizedState, current); // WHAT: Persist the updated aggregate for the state bucket.
      });

      const rankedStates = Array.from(aggregates.entries())
        .filter(([state]) => state !== 'UNKNOWN' || aggregates.size === 1) // WHAT: Drop unknown bucket unless it is the only entry.
        .sort((a, b) => b[1].count - a[1].count); // WHAT: Order states descending by asset count to highlight top regions.

      const topStates = rankedStates.slice(0, 15); // WHAT: Show up to fifteen states so the state list fills more vertical space.
      const maxCount = topStates.reduce((acc, entry) => Math.max(acc, entry[1].count), 0) || 1; // WHAT: Avoid division by zero when computing progress percentages.

      return topStates.map(([state, info], index) => {
        const progressPercent = Math.round((info.count / maxCount) * 100); // WHAT: Derive progress relative to highest-count state.
        return {
          id: `${state}-${index}`, // WHAT: Deterministic identifier combining state code and index for Vue rendering.
          label: state === 'UNKNOWN' ? 'Unknown State' : state, // WHAT: Present readable label while preserving fallback messaging.
          count: info.count, // WHAT: Total assets aggregated for the state.
          progressPercent,
          maxCount, // WHAT: Include maxCount for ARIA context even though shared across entries.
        };
      });
    });

    function onStatusFilterChange(): void {
      // WHAT: Handler for asset master status filter change
      // WHY: Refetch markers with the selected status filter
      dispersionStore.clearCache(); // WHAT: Clear cache to force fresh fetch with new filter
      const params = selectedStatus.value ? { asset_status: selectedStatus.value } : {}; // WHAT: Build query params with asset_status filter
      dispersionStore.fetchMarkers(params); // WHAT: Fetch markers with the selected filter
    }

    onMounted(() => {
      dispersionStore.clearCache(); // WHAT: Ensure fresh data is fetched when the component mounts.
      dispersionStore.fetchMarkers(); // WHAT: Load one marker per asset from the backend without clustering params (defaults to all).
    });

    // WHAT: Bubble marker-click events upward so the dashboard page can reuse the AM asset modal.
    function handleMarkerClick(payload: { assetHubId: string | number; address?: string | null }): void {
      emit('marker-click', payload)
    }

    return {
      mapMarkers, // WHAT: Expose computed markers to template for map rendering.
      markerSummaries, // WHAT: Expose density summaries for the list section.
      selectedStatus, // WHAT: Expose reactive filter state for v-model binding.
      onStatusFilterChange, // WHAT: Expose handler for filter change event.
      handleMarkerClick, // WHAT: Expose marker click handler for VectorMap.
    };
  },
});
</script>
