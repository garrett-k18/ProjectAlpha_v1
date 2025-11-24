<template>
  <BModal
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :title="entry ? 'Edit GL Entry' : 'Create GL Entry'"
    size="xl"
    centered
  >
    <div class="alert alert-info">
      <i class="mdi mdi-information"></i>
      This is a prototype form. Full entry creation/editing functionality coming soon!
    </div>
    
    <div class="row g-3">
      <div class="col-md-6">
        <label class="form-label">Entry Number *</label>
        <input v-model="formData.entry" type="text" class="form-control" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Company Name *</label>
        <input v-model="formData.company_name" type="text" class="form-control" required />
      </div>
      
      <div class="col-md-4">
        <label class="form-label">Posting Date *</label>
        <input v-model="formData.posting_date" type="date" class="form-control" required />
      </div>
      <div class="col-md-4">
        <label class="form-label">Account Number *</label>
        <input v-model="formData.account_number" type="text" class="form-control" required />
      </div>
      <div class="col-md-4">
        <label class="form-label">Account Name *</label>
        <input v-model="formData.account_name" type="text" class="form-control" required />
      </div>
      
      <div class="col-md-6">
        <label class="form-label">Debit Amount</label>
        <input v-model="formData.debit_amount" type="number" step="0.01" class="form-control" />
      </div>
      <div class="col-md-6">
        <label class="form-label">Credit Amount</label>
        <input v-model="formData.credit_amount" type="number" step="0.01" class="form-control" />
      </div>
      
      <div class="col-md-6">
        <label class="form-label">Tag</label>
        <select v-model="formData.tag" class="form-select">
          <option :value="null">Select Tag</option>
          <option value="loan_origination">Loan Origination</option>
          <option value="loan_payment">Loan Payment</option>
          <option value="property_acquisition">Property Acquisition</option>
        </select>
      </div>
      <div class="col-md-6">
        <label class="form-label">Bucket</label>
        <select v-model="formData.bucket" class="form-select">
          <option :value="null">Select Bucket</option>
          <option value="acquisition">Acquisition</option>
          <option value="servicing">Servicing</option>
          <option value="asset_management">Asset Management</option>
        </select>
      </div>
      
      <div class="col-12">
        <label class="form-label">Description</label>
        <textarea v-model="formData.description" class="form-control" rows="3"></textarea>
      </div>
    </div>

    <template #footer>
      <button class="btn btn-secondary" @click="$emit('update:modelValue', false)">
        Cancel
      </button>
      <button class="btn btn-primary" @click="handleSave">
        <i class="mdi mdi-content-save"></i> Save Entry
      </button>
    </template>
  </BModal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { BModal } from 'bootstrap-vue-next'
import type { GLEntry } from '@/stores/generalLedger'

const props = defineProps<{
  modelValue: boolean
  entry: GLEntry | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', data: Partial<GLEntry>): void
}>()

const formData = ref<Partial<GLEntry>>({
  entry: '',
  company_name: '',
  posting_date: new Date().toISOString().split('T')[0],
  entry_date: new Date().toISOString().split('T')[0],
  account_number: '',
  account_name: '',
  debit_amount: '0.00',
  credit_amount: '0.00',
  tag: null,
  bucket: null,
  description: '',
})

watch(() => props.entry, (newEntry) => {
  if (newEntry) {
    formData.value = { ...newEntry }
  }
}, { immediate: true })

function handleSave(): void {
  emit('save', formData.value)
}
</script>

