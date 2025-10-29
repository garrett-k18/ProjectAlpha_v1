<template>
  <div class="card">
    <div class="card-header">
      <h4 class="header-title">Geographic Distribution</h4>
    </div>
    <div class="card-body">
      <div v-if="loadingChart" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
        <p class="text-muted mt-2">Loading geographic data...</p>
      </div>
      <div v-else-if="!chartData || chartData.length === 0" class="text-center py-5 text-muted">
        <i class="mdi mdi-map-marker-outline fs-1 mb-3 d-block"></i>
        <p>No geographic data available</p>
      </div>
      <div v-else>
        <b-row>
          <b-col lg="8">
            <div class="map-placeholder bg-light text-center d-flex align-items-center justify-content-center" 
              style="height: 500px; border-radius: 8px;">
              <div>
                <i class="mdi mdi-map fs-1 text-muted mb-2"></i>
                <p class="text-muted mb-0">Map visualization placeholder</p>
                <small class="text-muted">Integrate jVectorMap or similar library</small>
              </div>
            </div>
          </b-col>
          <b-col lg="4">
            <h5 class="mb-3">Top States</h5>
            <div class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>State</th>
                    <th class="text-end">Count</th>
                    <th class="text-end">UPB</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(state, index) in chartData.slice(0, 10)" :key="index"
                    @click="handleDrillDown(state)" style="cursor: pointer;">
                    <td class="fw-semibold">{{ state.x }}</td>
                    <td class="text-end">{{ state.meta?.count || 0 }}</td>
                    <td class="text-end">{{ formatCurrency(state.y) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </b-col>
        </b-row>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  chartData: any[]
  gridData: any[]
  loadingChart: boolean
  loadingGrid: boolean
}>()

const emit = defineEmits<{
  (e: 'drill-down', payload: { type: string; data: any }): void
}>()

function handleDrillDown(state: any): void {
  emit('drill-down', { type: 'state', data: state })
}

function formatCurrency(value: number): string {
  const abs = Math.abs(value || 0)
  if (abs >= 1_000_000) return `$${(abs / 1_000_000).toFixed(1)}MM`
  return `$${abs.toFixed(0)}`
}
</script>
