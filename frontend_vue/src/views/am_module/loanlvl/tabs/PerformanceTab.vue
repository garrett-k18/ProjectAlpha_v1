<template>
  <!-- WHAT: Performance tab wrapper using PLMetrics component -->
  <!-- WHY: Container for P&L metrics with header and asset context -->
  <!-- HOW: Imports PLMetrics component and passes row/productId props -->
  <!-- WHERE: Used in loan-level tabs (frontend_vue/src/views/am_module/loanlvl/tabs/) -->
  <div class="container-fluid px-0">
    <!-- WHAT: Hyper UI stat widgets for key cash flow metrics -->
    <!-- WHY: Quick overview at the top of the page -->
    <PerformanceWidgets :asset-hub-id="assetHubId" />

    <div class="card shadow mt-4">
      

      <div class="card-body">
        <!-- WHAT: PLMetrics component - 3-column P&L grid -->
        <!-- WHY: Reusable component for Underwritten vs Realized comparison -->
        <!-- WHERE: Component at frontend_vue/src/views/am_module/loanlvl/tabs/components/PLMetrics.vue -->
        <PLMetrics :row="row" :asset-hub-id="assetHubId" />
      </div>
    </div>

    <!-- WHAT: Cash Flow Series component - time-series grid -->
    <!-- WHY: Show period-by-period cash flows for detailed analysis -->
    <!-- WHERE: Component at frontend_vue/src/views/am_module/loanlvl/tabs/components/CashFlowSeries.vue -->
    <div class="card shadow mt-4">
      <div class="card-body">
        <CashFlowSeries :asset-hub-id="assetHubId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Performance tab container that uses PLMetrics component
// WHY: Separates layout/header from metrics logic for modularity
// HOW: Imports PLMetrics and passes props through
// NOTE: PLMetrics handles all calculations and data - this is just the wrapper
import PLMetrics from '../performance/PLMetrics.vue'
import CashFlowSeries from '../performance/CashFlowSeries.vue'
import PerformanceWidgets from '../performance/PerformanceWidgets.vue'

// WHAT: Props interface for parent data
// WHY: Accept row data and asset hub ID to pass to PLMetrics
// HOW: Optional row and assetHubId props with null defaults
const props = withDefaults(defineProps<{ 
  row?: Record<string, any> | null
  assetHubId?: string | number | null 
}>(), {
  row: null,
  assetHubId: null,
})
</script>

<style scoped>
/* No custom styles needed - all styling is in PLMetrics component */
</style>
