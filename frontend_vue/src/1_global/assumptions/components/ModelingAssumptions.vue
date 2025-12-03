<template>
  <div class="modeling-assumptions-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Modeling Assumptions</h5>
        <p class="text-muted small mb-0">Global parameters used across models</p>
      </div>
      <div class="d-flex gap-2">
        <button
          class="btn btn-sm btn-primary"
          @click="saveChanges"
          :disabled="!hasChanges || isSaving || isLoading"
        >
          <i class="mdi mdi-content-save me-1"></i>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="text-muted small mb-2">Loading modeling assumptions...</div>
    <div v-else>
      <div v-if="loadError" class="alert alert-warning py-1 px-2 small mb-3">
        {{ loadError }}
      </div>

      <div class="row g-3">
        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Purchase Price (% of UPB)</label>
          <div class="input-group">
            <input
              type="number"
              step="0.01"
              min="0"
              class="form-control"
              :disabled="isSaving"
              v-model="form.default_pct_upb"
              @change="markAsChanged"
            />
            <span class="input-group-text">%</span>
          </div>
        </div>

        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Discount Rate (decimal)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_discount_rate"
            @change="markAsChanged"
          />
        </div>

        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Perf/RPL Hold Period (months)</label>
          <input
            type="number"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_perf_rpl_hold_period"
            @change="markAsChanged"
          />
        </div>
      </div>

      <hr class="my-3" />

      <div class="row g-3">
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Rate (decimal)</label>
          <input
            type="number"
            step="0.0001"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_rate"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Legal Term (months)</label>
          <input
            type="number"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_legal_term"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Amort Term (months)</label>
          <input
            type="number"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_amort_term"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Max Mod LTV (decimal)</label>
          <input
            type="number"
            step="0.0001"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_max_mod_ltv"
            @change="markAsChanged"
          />
        </div>

        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Interest-Only Flag</label>
          <select
            class="form-select"
            :disabled="isSaving"
            v-model="form.default_mod_io_flag"
            @change="markAsChanged"
          >
            <option :value="false">No</option>
            <option :value="true">Yes</option>
          </select>
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Down Payment (decimal)</label>
          <input
            type="number"
            step="0.0001"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_down_pmt"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Origination Cost ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_orig_cost"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Setup Duration (months)</label>
          <input
            type="number"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_setup_duration"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-3">
          <label class="form-label fw-medium">Mod Hold Duration (months)</label>
          <input
            type="number"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_mod_hold_duration"
            @change="markAsChanged"
          />
        </div>
      </div>

      <hr class="my-3" />

      <div class="row g-3">
        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Acq Legal Cost ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_acq_legal_cost"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Acq DD Cost ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_acq_dd_cost"
            @change="markAsChanged"
          />
        </div>
        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">Acq Tax/Title Cost ($)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_acq_tax_title_cost"
            @change="markAsChanged"
          />
        </div>

        <div class="col-12 col-md-4">
          <label class="form-label fw-medium">AM Fee (decimal)</label>
          <input
            type="number"
            step="0.01"
            min="0"
            class="form-control"
            :disabled="isSaving"
            v-model="form.default_am_fee_pct"
            @change="markAsChanged"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '@/lib/http'

const emit = defineEmits<{ (e: 'changed'): void }>()

const hasChanges = ref(false)
const isSaving = ref(false)
const isLoading = ref(false)
const loadError = ref<string | null>(null)

const form = ref<any>({
  default_pct_upb: '',
  default_discount_rate: '',
  default_perf_rpl_hold_period: '',
  default_mod_rate: '',
  default_mod_legal_term: '',
  default_mod_amort_term: '',
  default_max_mod_ltv: '',
  default_mod_io_flag: false,
  default_mod_down_pmt: '',
  default_mod_orig_cost: '',
  default_mod_setup_duration: '',
  default_mod_hold_duration: '',
  default_acq_legal_cost: '',
  default_acq_dd_cost: '',
  default_acq_tax_title_cost: '',
  default_am_fee_pct: '',
})

async function loadDefaults() {
  isLoading.value = true
  loadError.value = null
  try {
    const resp = await http.get('/acq/assumption-defaults/')
    if (resp && resp.data) {
      const data = { ...resp.data }
      if (
        data.default_discount_rate !== null &&
        data.default_discount_rate !== undefined &&
        data.default_discount_rate !== ''
      ) {
        const discNumeric = Number(data.default_discount_rate)
        if (!Number.isNaN(discNumeric)) {
          data.default_discount_rate = discNumeric.toFixed(2)
        }
      }
      if (
        data.default_am_fee_pct !== null &&
        data.default_am_fee_pct !== undefined &&
        data.default_am_fee_pct !== ''
      ) {
        const numeric = Number(data.default_am_fee_pct)
        if (!Number.isNaN(numeric)) {
          data.default_am_fee_pct = numeric.toFixed(2)
        }
      }
      form.value = { ...form.value, ...data }
    }
  } catch (e: any) {
    console.error('[ModelingAssumptions] load error', e)
    loadError.value = e?.message || 'Failed to load modeling assumptions'
  } finally {
    isLoading.value = false
  }
}

function markAsChanged() {
  hasChanges.value = true
  emit('changed')
}

async function saveChanges() {
  if (!hasChanges.value) return
  isSaving.value = true
  try {
    const resp = await http.patch('/acq/assumption-defaults/update/', form.value)
    if (resp && resp.data) {
      form.value = { ...form.value, ...resp.data }
    }
    hasChanges.value = false
  } catch (e) {
    console.error('[ModelingAssumptions] save error', e)
  } finally {
    isSaving.value = false
  }
}

onMounted(loadDefaults)
</script>

<style scoped>
.modeling-assumptions-container {
  min-height: 200px;
}
</style>
