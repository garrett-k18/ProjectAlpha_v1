<template>
  <div class="acquisition-analysis-tab">
    <div class="row g-3">
      <!-- Asset Snapshot - 20% width -->
      <div class="col-md-3 col-xl-2">
        <AssetSnapshot 
          :row="row" 
          :recommendations="recommendations" 
          :loading-recommendations="loadingRecommendations"
          @open-trade-assumptions="handleOpenTradeAssumptions"
        />
      </div>

      <!-- Model Outcomes and Model Cards - 80% width -->
      <div class="col-md-9 col-xl-10">
        <ModelOutcomes 
          :recommendations="recommendations" 
          :loading-recommendations="loadingRecommendations"
          :row="row"
          :asset-id="assetId"
          @models-changed="handleModelsChanged"
        />
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AssetSnapshot from '@/views/acq_module/loanlvl/components/model/assetSnapshot.vue'
import ModelOutcomes from '@/views/acq_module/loanlvl/components/model/ModelOutcomes.vue'
import http from '@/lib/http'

const props = withDefaults(defineProps<{
  row?: Record<string, any> | null
  assetId?: string | number | null
  module?: 'acq' | 'am'
}>(), {
  row: null,
  assetId: null,
  module: 'acq'
})

console.log('[AcquisitionAnalysisTab] MOUNTED with props assetId=', props.assetId, 'row=', props.row)

// WHAT: Router instance for navigation
const router = useRouter()

// WHAT: Backend recommendations state
const recommendations = ref<any>(null)
const loadingRecommendations = ref(false)

// WHAT: Handle trade assumptions button click from AssetSnapshot
function handleOpenTradeAssumptions(tradeId: number | string) {
  // WHAT: Navigate to trade dashboard with trade assumptions modal open
  // WHY: Trade assumptions modal is in the main dashboard, so we navigate there
  // HOW: Use query parameter to indicate modal should open
  router.push({
    name: 'acq-dash',
    query: { 
      trade: tradeId,
      openModal: 'trade-assumptions'
    }
  })
}

// WHAT: Fetch recommendations from backend API
async function fetchRecommendations() {
  if (!props.assetId) {
    console.warn('[AcquisitionAnalysisTab] No assetId provided, cannot fetch recommendations')
    return
  }

  loadingRecommendations.value = true
  try {
    const url = `/${props.module}/assets/${props.assetId}/model-recommendations/`
    console.log('[AcquisitionAnalysisTab] Fetching recommendations from:', url)
    const response = await http.get(url)
    recommendations.value = response.data
    console.log('[AcquisitionAnalysisTab] Received recommendations:', recommendations.value)
    console.log('[AcquisitionAnalysisTab] Metrics:', recommendations.value?.metrics)
  } catch (error: any) {
    console.error('[AcquisitionAnalysisTab] Failed to fetch recommendations:', error)
    console.error('[AcquisitionAnalysisTab] Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url
    })
    recommendations.value = null
  } finally {
    loadingRecommendations.value = false
  }
}

// WHAT: Handle model changes from the ModelOutcomes component
function handleModelsChanged(selectedModels: Set<string>, probabilities: Record<string, number>) {
  console.log('[AcquisitionAnalysisTab] Models changed:', selectedModels, probabilities)
  // Here you can add any additional logic needed when models change
  // For example, triggering calculations, saving to backend, etc.
}

// WHAT: Watch for assetId changes and fetch recommendations
watch(() => props.assetId, (newAssetId) => {
  if (newAssetId) {
    console.log('[AcquisitionAnalysisTab] AssetId changed to:', newAssetId, 'fetching recommendations...')
    fetchRecommendations()
  }
}, { immediate: true })

// WHAT: Lifecycle hook to fetch recommendations on component mount
onMounted(() => {
  if (props.assetId) {
    fetchRecommendations()
  }
})

watch(() => props.assetId, (newId) => {
  if (newId) {
    fetchRecommendations()
  }
})

</script>

<style scoped>
/* Button size adjustments */
.btn-xs {
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  line-height: 1.2;
}

/* Smooth transitions for expandable sections */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
