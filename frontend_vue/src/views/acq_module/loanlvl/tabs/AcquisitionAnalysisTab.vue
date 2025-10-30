<template>
  <div class="acquisition-analysis-tab">
    <!-- Asset Snapshot spanning full width -->
    <AssetSnapshot :row="row" :recommendations="recommendations" :loading-recommendations="loadingRecommendations" />

    <!-- Model Outcomes Component -->
    <ModelOutcomes 
      :recommendations="recommendations" 
      :loading-recommendations="loadingRecommendations"
      @models-changed="handleModelsChanged"
    />
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps, ref, onMounted, watch } from 'vue'
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

// WHAT: Backend recommendations state
const recommendations = ref<any>(null)
const loadingRecommendations = ref(false)

// WHAT: Fetch recommendations from backend API
async function fetchRecommendations() {
  if (!props.assetId) {
    console.warn('[AcquisitionAnalysisTab] No assetId provided, cannot fetch recommendations')
    return
  }

  loadingRecommendations.value = true
  try {
    const response = await http.get(`/${props.module}/assets/${props.assetId}/model-recommendations/`)
    recommendations.value = response.data
    console.log('[AcquisitionAnalysisTab] Received recommendations:', recommendations.value)
  } catch (error) {
    console.error('[AcquisitionAnalysisTab] Failed to fetch recommendations:', error)
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
