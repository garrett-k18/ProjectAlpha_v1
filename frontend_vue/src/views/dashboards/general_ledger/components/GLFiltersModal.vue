<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Filter GL Entries"
    size="lg"
    centered
  >
    <div class="row g-3">
      <!-- Date Filters -->
      <div class="col-md-6">
        <label class="form-label">Posting Date From</label>
        <input v-model="localFilters.posting_date_start" type="date" class="form-control" />
      </div>
      <div class="col-md-6">
        <label class="form-label">Posting Date To</label>
        <input v-model="localFilters.posting_date_end" type="date" class="form-control" />
      </div>

      <!-- Tag Filter -->
      <div class="col-md-6">
        <label class="form-label">Tag</label>
        <select v-model="localFilters.tag" class="form-select">
          <option :value="null">All Tags</option>
          <option value="loan_origination">Loan Origination</option>
          <option value="loan_payment">Loan Payment</option>
          <option value="property_acquisition">Property Acquisition</option>
          <option value="property_disposition">Property Disposition</option>
          <option value="operating_expense">Operating Expense</option>
          <option value="interest_income">Interest Income</option>
          <option value="interest_expense">Interest Expense</option>
        </select>
      </div>

      <!-- Bucket Filter -->
      <div class="col-md-6">
        <label class="form-label">Bucket</label>
        <select v-model="localFilters.bucket" class="form-select">
          <option :value="null">All Buckets</option>
          <option value="acquisition">Acquisition</option>
          <option value="servicing">Servicing</option>
          <option value="asset_management">Asset Management</option>
          <option value="disposition">Disposition</option>
          <option value="capital_markets">Capital Markets</option>
        </select>
      </div>

      <!-- Text Filters -->
      <div class="col-md-6">
        <label class="form-label">Company Name</label>
        <input v-model="localFilters.company_name" type="text" class="form-control" />
      </div>
      <div class="col-md-6">
        <label class="form-label">Loan Number</label>
        <input v-model="localFilters.loan_number" type="text" class="form-control" />
      </div>
    </div>

    <template #footer>
      <button class="btn btn-secondary" @click="handleReset">
        <i class="mdi mdi-refresh"></i> Reset
      </button>
      <button class="btn btn-primary" @click="handleApply">
        <i class="mdi mdi-check"></i> Apply Filters
      </button>
    </template>
  </BModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { BModal } from 'bootstrap-vue-next'
import type { GLEntryFilters } from '@/stores/generalLedger'

const props = defineProps<{
  modelValue: boolean
  filters: GLEntryFilters
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'apply', filters: GLEntryFilters): void
  (e: 'reset'): void
}>()

const localFilters = ref<GLEntryFilters>({ ...props.filters })

watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

function handleApply(): void {
  emit('apply', localFilters.value)
}

function handleReset(): void {
  localFilters.value = {}
  emit('reset')
}
</script>

