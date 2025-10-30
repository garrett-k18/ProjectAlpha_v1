<template>
  <div class="acquisition-analysis-tab">
    <!-- Asset Snapshot spanning full width -->
    <AssetSnapshot :row="row" />

    <div class="row g-3">
      <!-- Left Column: Assumptions Summary -->
      <div class="col-lg-6">
        <AssumptionsSummary
          :fcTimeline="fcTimeline"
          :commercialUnits="commercialUnits"
        />
      </div>

      <!-- Right Column: Investment Metrics -->
      <div class="col-lg-6">
        <InvestmentMetrics :row="row" :assetId="assetId" />
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, onMounted } from 'vue'
import AssumptionsSummary from '@/views/acq_module/loanlvl/components/model/assumptionsSummary.vue'
import AssetSnapshot from '@/views/acq_module/loanlvl/components/model/assetSnapshot.vue'
import InvestmentMetrics from '@/views/acq_module/loanlvl/components/InvestmentMetrics.vue'

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
}>(), {
  row: null,
  assetId: null,
})

console.log('[AcquisitionAnalysisTab] MOUNTED with props assetId=', props.assetId, 'row=', props.row)

// State for summary props
const fcTimeline = ref<any | null>(null)
const commercialUnits = ref<any[]>([])

// Fetch data from existing DRF endpoints
async function loadSummaryData() {
  try {
    // Commercial units
    const cuRes = await fetch('/api/core/commercial-units/', { credentials: 'include' })
    commercialUnits.value = await cuRes.json()

    // Asset-scoped FC timeline
    const id = props.assetId != null ? String(props.assetId) : ''
    console.log('[AcquisitionAnalysisTab] assetId=', props.assetId, 'using id=', id)
    if (id) {
      const fcRes = await fetch(`/api/acq/assets/${id}/fc-timeline/`, { credentials: 'include' })
      console.log('[AcquisitionAnalysisTab] FC timeline fetch status=', fcRes.status, 'ok=', fcRes.ok)
      if (fcRes.ok) fcTimeline.value = await fcRes.json()
      else fcTimeline.value = null
      console.log('[AcquisitionAnalysisTab] fcTimeline=', fcTimeline.value)
    } else {
      fcTimeline.value = null
      console.log('[AcquisitionAnalysisTab] No id provided, fcTimeline set to null')
    }
  } catch (e) {
    console.warn('Failed to load acquisition assumptions summary', e)
  }
}

onMounted(loadSummaryData)
</script>
