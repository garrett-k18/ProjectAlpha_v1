<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    size="xl"
    :title="modalTitle"
    centered
    @hidden="handleClose"
  >
    <div class="drill-down-content">
      <component
        :is="currentDrillDownComponent"
        :data="drillDownData"
      />
    </div>

    <template #footer>
      <div class="d-flex justify-content-between w-100">
        <button class="btn btn-secondary" @click="handleClose">
          <i class="mdi mdi-close me-1"></i>
          Close
        </button>
        <button class="btn btn-primary" @click="handleExportDrillDown">
          <i class="mdi mdi-download me-1"></i>
          Export Details
        </button>
      </div>
    </template>
  </BModal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { BModal } from 'bootstrap-vue-next'
import TradeDetails from '../drilldowns/TradeDetails.vue'
import StatusDetails from '../drilldowns/StatusDetails.vue'
import AssetDetails from '../drilldowns/AssetDetails.vue'

const props = defineProps<{
  modelValue: boolean
  drillDownType: string
  drillDownData: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'close'): void
}>()

const modalTitle = computed<string>(() => {
  const typeLabels: Record<string, string> = {
    'trade': 'Trade Details',
    'status': 'Status Analysis',
    'asset': 'Asset Breakdown',
    'state': 'State Details',
    'timeseries': 'Trend Analysis',
  }
  return typeLabels[props.drillDownType] || 'Details'
})

const currentDrillDownComponent = computed(() => {
  const componentMap: Record<string, any> = {
    'trade': TradeDetails,
    'status': StatusDetails,
    'asset': AssetDetails,
    'state': AssetDetails,
    'timeseries': AssetDetails,
  }
  return componentMap[props.drillDownType] || AssetDetails
})

function handleClose(): void {
  emit('close')
}

function handleExportDrillDown(): void {
  console.log('[DrillDownModal] Export drill-down:', props.drillDownType, props.drillDownData)
  alert('Export drill-down details coming soon!')
}
</script>

<style scoped>
.drill-down-content {
  min-height: 300px;
  max-height: 600px;
  overflow-y: auto;
}
</style>
