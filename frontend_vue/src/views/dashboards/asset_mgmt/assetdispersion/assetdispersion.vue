<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Asset Dispersion</h4>
    </div>

    <div class="card-body py-0">
      <div class="mb-4 mt-3">
        <!-- WHAT: Render jsVectorMap via wrapper with backend-driven markers for active assets only. -->
        <VectorMap 
          id="am-dispersion-map" 
          :map-height="217" 
          :location-data="mapMarkers"
          :marker-color="'#727cf5'"
        />
      </div>

      <!-- WHAT: Present marker density summary to replace previous static progress bands. -->
      <div v-if="markerSummaries.length > 0" v-for="summary in markerSummaries" :key="summary.id">
        <h5 class="mb-1 mt-0 fw-normal">{{ summary.label }}</h5>
        <div class="progress-w-percent d-flex align-items-center gap-2"> <!-- WHAT: Flex container keeps bar and count on a single horizontal line. -->
          <!-- WHAT: Cap bar width so count text remains within card boundaries regardless of large asset totals. -->
          <div class="progress progress-sm flex-grow-1 mb-0" style="max-width: 85%;">
            <div
              class="progress-bar"
              role="progressbar"
              :style="`width: ${summary.progressPercent}%;`"
              :aria-valuenow="summary.count"
              aria-valuemin="0"
              :aria-valuemax="summary.maxCount"
            ></div>
          </div>
          <span class="progress-value fw-bold text-nowrap">{{ summary.count }} assets</span> <!-- WHAT: Right-align count text and prevent wrapping. -->
        </div>
      </div>

      <!-- WHAT: Display graceful fallback when zero markers are returned (e.g., filters exclude all assets). -->
      <div v-else class="py-3 text-center text-muted">
        No active assets found for the current filters.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'; // WHAT: Vue APIs for component definition, derived state, and lifecycle hooks.
import VectorMap from "./vectorMap.vue"; // WHAT: Local wrapper around jsVectorMap for US projection rendering.
import { useAssetDispersionStore } from '@/stores/assetDispersion'; // WHAT: Pinia store supplying backend-driven dispersion markers.

export default defineComponent({
  name: 'AssetDispersion', // WHAT: Component identifier updated to match file rename for clearer Vue devtools labeling.
  components: { VectorMap }, // WHAT: Register child components required by the template.
  setup() {
    const dispersionStore = useAssetDispersionStore(); // WHAT: Instantiate the Pinia store to access markers/actions.

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

      const topFive = rankedStates.slice(0, 5); // WHAT: Limit display to the states with the highest asset totals.
      const maxCount = topFive.reduce((acc, entry) => Math.max(acc, entry[1].count), 0) || 1; // WHAT: Avoid division by zero when computing progress percentages.

      return topFive.map(([state, info], index) => {
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

    onMounted(() => {
      dispersionStore.clearCache(); // WHAT: Ensure fresh data is fetched when the component mounts.
      dispersionStore.fetchMarkers(); // WHAT: Load one marker per asset from the backend without clustering params.
    });

    return {
      mapMarkers, // WHAT: Expose computed markers to template for map rendering.
      markerSummaries, // WHAT: Expose density summaries for the list section.
    };
  },
});
</script>
