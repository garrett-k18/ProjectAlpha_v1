<template>
  <!--
    CommercialAssetAssumptions.vue
    What: CRUD table for Commercial Units scaling factors (fc_cost_scale, rehab_cost_scale, rehab_duration_scale).
    Why: Allows editing multipliers by unit count as defined in `CommercialUnits` model.
    Where: frontend_vue/src/1_global/assumptions/components/CommercialAssetAssumptions.vue
    How: Uses DRF endpoints under /api/core/commercial-units/ (GET, POST, PATCH, DELETE).
  -->
  <div class="commercial-asset-assumptions-container">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-1">Commercial Asset Assumptions</h5>
        <p class="text-muted small mb-0">Scaling multipliers by unit count</p>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-secondary" @click="addRow"><i class="mdi mdi-plus me-1"></i>Add Row</button>
        <button 
          class="btn btn-sm btn-primary"
          @click="saveChanges"
          :disabled="!hasChanges || isSaving"
        >
          <i class="mdi mdi-content-save me-1"></i>
          {{ isSaving ? 'Saving...' : 'Save' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>
      <p class="text-muted mt-2">Loading commercial unit scalings...</p>
    </div>

    <!-- Table -->
    <div v-else class="table-responsive">
      <table class="table table-sm align-middle">
        <thead>
          <tr>
            <th style="width: 120px;">Units</th>
            <th style="width: 220px;">FC Cost Scale</th>
            <th style="width: 220px;">Rehab Cost Scale</th>
            <th style="width: 240px;">Rehab Duration Scale</th>
            <th style="width: 100px;"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in rows" :key="row.localKey">
            <td>
              <input type="number" class="form-control form-control-sm" v-model.number="row.units" @input="markChanged" min="1" step="1" />
            </td>
            <td>
              <div class="input-group input-group-sm">
                <input type="number" class="form-control" v-model.number="row.fcCostScale" @input="markChanged" min="0" step="0.01" />
                <span class="input-group-text">x</span>
              </div>
            </td>
            <td>
              <div class="input-group input-group-sm">
                <input type="number" class="form-control" v-model.number="row.rehabCostScale" @input="markChanged" min="0" step="0.01" />
                <span class="input-group-text">x</span>
              </div>
            </td>
            <td>
              <div class="input-group input-group-sm">
                <input type="number" class="form-control" v-model.number="row.rehabDurationScale" @input="markChanged" min="0" step="0.01" />
                <span class="input-group-text">x</span>
              </div>
            </td>
            <td class="text-end">
              <button class="btn btn-xs btn-outline-danger" @click="removeRow(idx, row)"><i class="mdi mdi-trash-can-outline"></i></button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="text-muted small">Tip: Scales are multipliers (e.g., 1.30 = 130%).</div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
/**
 * What/Why/Where/How (developer notes):
 * - What: Inline-editable table for `CommercialUnits` multipliers.
 * - Why: Mirrors backend model `CommercialUnits` to control cost/duration scaling by unit count.
 * - Where: assumptions hub → Commercial Asset Assumptions tab.
 * - How: Fetch list (GET), upsert changes (POST/PATCH), delete rows (DELETE) via /api/core/commercial-units/.
 */
import { ref, reactive, onMounted } from 'vue'
const emit = defineEmits<{ (e: 'changed'): void }>()

// Row DTO matching serializer at `core/serializers/assumptions.py::CommercialUnitsSerializer`
interface UnitScaleRow {
  id: number | null
  units: number | null
  fcCostScale: number | null
  rehabCostScale: number | null
  rehabDurationScale: number | null
  // localKey only for Vue list rendering uniqueness
  localKey: string
}

// State
const isLoading = ref(true)
const isSaving = ref(false)
const hasChanges = ref(false)
const rows = reactive<UnitScaleRow[]>([])

// Helpers
function markChanged() {
  hasChanges.value = true
  emit('changed')
}

function newLocalRow(): UnitScaleRow {
  return {
    id: null,
    units: null,
    fcCostScale: 1.0,
    rehabCostScale: 1.0,
    rehabDurationScale: 1.0,
    localKey: Math.random().toString(36).slice(2),
  }
}

function addRow() {
  rows.push(newLocalRow())
  markChanged()
}

async function removeRow(index: number, row: UnitScaleRow) {
  // If it's an existing row in DB, delete via API; otherwise just remove locally
  try {
    if (row.id) {
      const resp = await fetch(`/api/core/commercial-units/${row.id}/`, {
        method: 'DELETE',
        credentials: 'include',
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    }
    rows.splice(index, 1)
    markChanged()
  } catch (err) {
    console.error('Failed to delete row:', err)
    alert('Failed to delete row')
  }
}

async function loadRows() {
  isLoading.value = true
  try {
    const resp = await fetch('/api/core/commercial-units/', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    rows.splice(0, rows.length, ...data.map((d: any) => ({ ...d, localKey: `${d.id}` })))
  } catch (err) {
    console.error('Error loading commercial units:', err)
  } finally {
    isLoading.value = false
    hasChanges.value = false
  }
}

async function saveChanges() {
  isSaving.value = true
  try {
    // Persist rows: POST new (id null), PATCH existing
    const ops = rows.map(async (r) => {
      const payload = {
        units: r.units,
        fcCostScale: r.fcCostScale,
        rehabCostScale: r.rehabCostScale,
        rehabDurationScale: r.rehabDurationScale,
      }
      if (!r.id) {
        const resp = await fetch('/api/core/commercial-units/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload),
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const created = await resp.json()
        r.id = created.id
        r.localKey = `${created.id}`
      } else {
        const resp = await fetch(`/api/core/commercial-units/${r.id}/`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload),
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      }
    })
    await Promise.all(ops)
    hasChanges.value = false
  } catch (err) {
    console.error('Failed to save changes:', err)
    alert('Failed to save changes')
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadRows()
})
</script>

<style scoped>
.commercial-asset-assumptions-container {
  min-height: 200px;
}
.table td, .table th { vertical-align: middle; }
</style>
