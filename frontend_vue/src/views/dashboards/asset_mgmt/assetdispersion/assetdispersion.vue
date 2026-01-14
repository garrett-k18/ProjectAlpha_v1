<template>
  <div class="card h-100 flex-grow-1 w-100 border-0 shadow-sm">
    <div class="d-flex card-header bg-transparent border-0 justify-content-between align-items-center pt-3 px-3">
      <h4 class="header-title mb-0 text-primary-navy fw-bold">Asset Dispersion</h4>
      <!-- Filter dropdown for asset master status -->
      <div class="d-flex align-items-center gap-2">
        <label for="assetStatusFilter" class="small mb-0 text-muted">Filter</label>
        <select 
          id="assetStatusFilter" 
          class="form-select form-select-sm" 
          v-model="selectedStatus" 
          @change="onStatusFilterChange"
          style="width: auto; border-radius: 6px;"
          :disabled="isLoading"
        >
          <option value="">All</option>
          <option value="ACTIVE">Active</option>
          <option value="LIQUIDATED">Liquidated</option>
        </select>
      </div>
    </div>

    <div class="card-body p-3 d-flex flex-column justify-content-center" style="min-height: 480px;">
      <!-- Loading State: Show spinner only -->
      <div v-if="isLoading" class="d-flex justify-content-center align-items-center h-100">
        <div class="text-center">
          <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
          <p class="text-muted small">Loading assets...</p>
        </div>
      </div>

      <!-- Loaded State: Show all content -->
      <div v-else class="row align-items-center g-0">
        <!-- WHAT: Left column – compact state summary bands stacked vertically -->
        <div
          v-if="markerSummaries.length > 0"
          class="col-12 col-lg-2 order-2 order-lg-1 mt-3 mt-lg-0 pe-lg-4"
        >
          <div class="mb-3">
            <span class="text-muted text-uppercase small fw-bold" style="letter-spacing: 0.05em;">Top States</span>
          </div>

          <div
            v-for="summary in markerSummaries"
            :key="summary.id"
            class="mb-3"
          >
            <div class="d-flex align-items-center justify-content-between gap-2 mb-1">
              <span class="text-dark small fw-bold" style="min-width: 1.5rem;">{{ summary.label }}</span>
              <span class="fw-bold text-primary-navy small">{{ summary.count }}</span>
            </div>
            <div class="progress progress-sm" style="height: 4px; background-color: rgba(0,0,0,0.05); border-radius: 4px;">
              <div
                class="progress-bar bg-primary"
                role="progressbar"
                :style="`width: ${summary.progressPercent}%; border-radius: 4px;`"
                :aria-valuenow="summary.count"
                aria-valuemin="0"
                :aria-valuemax="summary.maxCount"
              ></div>
            </div>
          </div>
        </div>

        <!-- WHAT: Right column – Centered US Map -->
        <div class="col-12 col-lg-10 order-1 order-lg-2">
          <div class="d-flex justify-content-center align-items-center">
            <div style="width: 100%; max-width: 820px;">
              <!-- WHAT: Render jsVectorMap via wrapper -->
              <VectorMap 
                v-if="markerSummaries.length > 0"
                id="am-dispersion-map" 
                :map-height="420" 
                :location-data="mapMarkers"
                :marker-color="'#727cf5'"
                @marker-click="handleMarkerClick"
              />
            </div>
          </div>

          <!-- WHAT: Display graceful fallback when zero markers are returned -->
          <div v-if="markerSummaries.length === 0" class="py-5 text-center text-muted">
            <i class="mdi mdi-map-marker-off d-block font-24 mb-2"></i>
            No active assets found for the current filters.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted, ref } from 'vue';
import VectorMap from "./vectorMap.vue";
import { useAssetDispersionStore } from '@/stores/assetDispersion';

/**
 * AssetDispersion
 * 
 * WHAT: Geographic visualization of asset distribution across US states with density ranking
 * WHY: Provides portfolio managers with regional portfolio concentration insights
 * HOW: Uses jsVectorMap for rendering + Pinia store for marker/state data, with v-if loading gate
 */
export default defineComponent({
  name: 'AssetDispersion',
  components: { VectorMap },
  setup(_, { emit }) {
    const dispersionStore = useAssetDispersionStore();
    const selectedStatus = ref<string>('');
    const isLoading = ref<boolean>(true);

    const mapMarkers = computed(() => dispersionStore.vectorMarkers);
    const rawMarkers = computed(() => dispersionStore.markers);

    const markerSummaries = computed(() => {
      const markersArray = Array.isArray(rawMarkers.value) ? rawMarkers.value : [];
      const aggregates = new Map<string, { count: number; stateLabel: string }>();

      markersArray.forEach((marker) => {
        const normalizedState = typeof marker.state === 'string' && marker.state.trim().length > 0 ? marker.state.trim().toUpperCase() : 'UNKNOWN';
        const current = aggregates.get(normalizedState) ?? { count: 0, stateLabel: normalizedState };
        current.count += Number(marker.count ?? 1);
        aggregates.set(normalizedState, current);
      });

      const rankedStates = Array.from(aggregates.entries())
        .filter(([state]) => state !== 'UNKNOWN' || aggregates.size === 1)
        .sort((a, b) => b[1].count - a[1].count);

      const topStates = rankedStates.slice(0, 10); // Reduced to top 10 for cleaner professional look
      const maxCount = topStates.reduce((acc, entry) => Math.max(acc, entry[1].count), 0) || 1;

      return topStates.map(([state, info], index) => {
        const progressPercent = Math.round((info.count / maxCount) * 100);
        return {
          id: `${state}-${index}`,
          label: state === 'UNKNOWN' ? 'Unknown' : state,
          count: info.count,
          progressPercent,
          maxCount,
        };
      });
    });

    function onStatusFilterChange(): void {
      isLoading.value = true;
      dispersionStore.clearCache();
      const params = selectedStatus.value ? { asset_status: selectedStatus.value } : {};
      dispersionStore.fetchMarkers(params).finally(() => {
        isLoading.value = false;
      });
    }

    onMounted(async () => {
      isLoading.value = true;
      dispersionStore.clearCache();
      try {
        await dispersionStore.fetchMarkers();
      } finally {
        isLoading.value = false;
      }
    });

    function handleMarkerClick(payload: { assetHubId: string | number; address?: string | null }): void {
      emit('marker-click', payload)
    }

    return {
      mapMarkers,
      markerSummaries,
      selectedStatus,
      isLoading,
      onStatusFilterChange,
      handleMarkerClick,
    };
  },
});
</script>

<style scoped>
.text-primary-navy {
  color: #1B3B5F;
}
.header-title {
  font-size: 1.1rem;
  letter-spacing: 0.02em;
}
</style>
