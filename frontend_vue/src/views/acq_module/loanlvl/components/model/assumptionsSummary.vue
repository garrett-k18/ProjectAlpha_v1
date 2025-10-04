<template>
  <!--
    assumptionsSummary.vue
    What: Presentational summary card(s) for modeling assumptions fed in via props.
    Why: Reuse in loan-level model views without duplicating fetch logic; parent provides data.
    Where: frontend_vue/src/views/acq_module/loanlvl/components/model/assumptionsSummary.vue
    How: Strongly-typed props mapping to backend serializers, with simple formatting helpers.
  -->
  <div class="assumptions-summary">
    <div class="card mb-3">
      <div class="card-body">
        <h5 class="card-title mb-2">Assumptions Summary</h5>
        

        <!-- Foreclosure Timeline Summary (by asset state) -->
        <div class="mb-2 d-flex align-items-baseline gap-2">
          <span class="text-muted">Total FC Duration:</span>
          <span class="fw-bold">
            {{ fcTimeline?.totalDurationDays ? Math.ceil(fcTimeline.totalDurationDays / 30) : '—' }} months
          </span>
        </div>

        <!-- REO Marketing Duration -->
        <div class="mb-2 d-flex align-items-baseline gap-2">
          <span class="text-muted">REO Marketing Duration:</span>
          <span class="fw-bold">{{ fcTimeline?.reoMarketingMonths ?? '—' }} months</span>
        </div>
        <hr />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Props-driven summary component. Parent fetches data from backend models/serializers and passes in.
 * Suggested sources:
 *  - CommercialUnits: `CommercialUnitsSerializer`
 */

import { computed } from 'vue'

// Types aligning with backend serializers
interface StatusTimelineItem { id: number; status: string; statusDisplay: string; durationDays: number | null }
interface AssetFCTimeline { state: string | null; statuses: StatusTimelineItem[]; totalDurationDays?: number | null; reoMarketingMonths?: number | null }

interface CommercialUnitRow {
  id: number
  units: number
  fcCostScale: number
  rehabCostScale: number
  rehabDurationScale: number
}

// Props (all optional to keep component flexible)
const props = defineProps<{
  fcTimeline?: AssetFCTimeline | null
  commercialUnits?: CommercialUnitRow[]
}>()

// Refs to props for template
const fcTimeline = computed(() => props.fcTimeline ?? null)
const commercialUnits = computed(() => props.commercialUnits ?? [])

// Formatting helpers
function currency0(v?: number | null): string {
  if (v === null || v === undefined) return '-'
  try { return `$${Number(v).toLocaleString('en-US', { maximumFractionDigits: 0 })}` } catch { return String(v) }
}
function percent2(v?: number | null): string {
  try { return `${Number(v).toFixed(2)}%` } catch { return String(v) }
}
function number2(v?: number | null): string {
  if (v === null || v === undefined) return '-'
  try { return Number(v).toFixed(2) } catch { return String(v) }
}
</script>

<style scoped>
.assumptions-summary :where(.card-title){ margin-bottom: 0.25rem; }
</style>
