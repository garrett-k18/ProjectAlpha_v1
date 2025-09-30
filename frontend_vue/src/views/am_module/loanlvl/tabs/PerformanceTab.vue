<template>
  <!-- WHAT: Performance tab wrapper using PLMetrics component -->
  <!-- WHY: Container for P&L metrics with header and asset context -->
  <!-- HOW: Imports PLMetrics component and passes row/productId props -->
  <!-- WHERE: Used in loan-level tabs (frontend_vue/src/views/am_module/loanlvl/tabs/) -->
  <div class="container-fluid px-0">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-body d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <i class="fas fa-chart-line text-muted"></i>
          <span class="fw-semibold">Performance Dashboard</span>
        </div>
        <div class="d-flex align-items-center gap-2 small text-muted">
          <span>Asset ID:</span>
          <span class="fw-medium">{{ productId ?? row?.asset_hub_id ?? '—' }}</span>
        </div>
      </div>

      <div class="card-body">
        <!-- WHAT: PLMetrics component - 3-column P&L grid -->
        <!-- WHY: Reusable component for Underwritten vs Realized comparison -->
        <!-- WHERE: Component at frontend_vue/src/views/am_module/loanlvl/tabs/components/PLMetrics.vue -->
        <PLMetrics :row="row" :product-id="productId" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Performance tab container that uses PLMetrics component
// WHY: Separates layout/header from metrics logic for modularity
// HOW: Imports PLMetrics and passes props through
// NOTE: PLMetrics handles all calculations and data - this is just the wrapper
import { withDefaults, defineProps } from 'vue'
import PLMetrics from './components/PLMetrics.vue'

// WHAT: Props interface for parent data
// WHY: Accept row data and asset ID to pass to PLMetrics
// HOW: Optional row and productId props with null defaults
withDefaults(defineProps<{ 
  row?: Record<string, any> | null
  productId?: string | number | null 
}>(), {
  row: null,
  productId: null,
})
</script>

<style scoped>
/* No custom styles needed - all styling is in PLMetrics component */
</style>
