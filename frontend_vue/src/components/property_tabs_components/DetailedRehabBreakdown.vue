<template>
  <!-- WHAT: Detailed Rehab Breakdown Component (Shared) -->
  <!-- WHY: Display/edit itemized rehab estimates from broker inspection -->
  <div class="detailed-rehab-breakdown">
    <!-- WHAT: Property address header -->
    <div v-if="showHeader" class="mb-3">
      <h6 class="text-muted mb-1">Property</h6>
      <p class="mb-0 fw-semibold">{{ formatAddress(asset) }}</p>
      <p class="mb-0 small text-muted">{{ formatCityState(asset) }}</p>
    </div>

    <hr v-if="showHeader">

    <!-- WHAT: Detailed rehab breakdown table -->
    <!-- WHY: Show table if data exists OR if in editable mode (to allow data entry) -->
    <div v-if="hasDetailedRehab(asset) || editable">
      <div class="table-responsive">
        <table class="table table-bordered mb-0">
          <thead class="table-light">
            <tr>
              <th>Rehab Category</th>
              <th class="text-center" style="width: 100px;">Grade</th>
              <th class="text-end" style="width: 150px;">Estimated Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="asset.broker_roof_est || editable">
              <td><i class="ri-home-gear-line me-2 text-muted"></i>Roof</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_roof_grade"
                  @change="handleGradeChange('broker_roof_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_roof_grade" :class="getGradeBadgeClass(asset.broker_roof_grade)">
                  {{ asset.broker_roof_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_roof_est)"
                  @input="handleCostChange('broker_roof_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_roof_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_kitchen_est || editable">
              <td><i class="ri-restaurant-line me-2 text-muted"></i>Kitchen</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_kitchen_grade"
                  @change="handleGradeChange('broker_kitchen_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_kitchen_grade" :class="getGradeBadgeClass(asset.broker_kitchen_grade)">
                  {{ asset.broker_kitchen_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_kitchen_est)"
                  @input="handleCostChange('broker_kitchen_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_kitchen_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_bath_est || editable">
              <td><i class="ri-contrast-drop-line me-2 text-muted"></i>Bathrooms</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_bath_grade"
                  @change="handleGradeChange('broker_bath_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_bath_grade" :class="getGradeBadgeClass(asset.broker_bath_grade)">
                  {{ asset.broker_bath_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_bath_est)"
                  @input="handleCostChange('broker_bath_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_bath_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_flooring_est || editable">
              <td><i class="ri-layout-grid-line me-2 text-muted"></i>Flooring</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_flooring_grade"
                  @change="handleGradeChange('broker_flooring_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_flooring_grade" :class="getGradeBadgeClass(asset.broker_flooring_grade)">
                  {{ asset.broker_flooring_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_flooring_est)"
                  @input="handleCostChange('broker_flooring_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_flooring_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_windows_est || editable">
              <td><i class="ri-window-line me-2 text-muted"></i>Windows</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_windows_grade"
                  @change="handleGradeChange('broker_windows_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_windows_grade" :class="getGradeBadgeClass(asset.broker_windows_grade)">
                  {{ asset.broker_windows_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_windows_est)"
                  @input="handleCostChange('broker_windows_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_windows_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_appliances_est || editable">
              <td><i class="ri-fridge-line me-2 text-muted"></i>Appliances</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_appliances_grade"
                  @change="handleGradeChange('broker_appliances_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_appliances_grade" :class="getGradeBadgeClass(asset.broker_appliances_grade)">
                  {{ asset.broker_appliances_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_appliances_est)"
                  @input="handleCostChange('broker_appliances_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_appliances_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_plumbing_est || editable">
              <td><i class="ri-water-flash-line me-2 text-muted"></i>Plumbing</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_plumbing_grade"
                  @change="handleGradeChange('broker_plumbing_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_plumbing_grade" :class="getGradeBadgeClass(asset.broker_plumbing_grade)">
                  {{ asset.broker_plumbing_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_plumbing_est)"
                  @input="handleCostChange('broker_plumbing_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_plumbing_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_electrical_est || editable">
              <td><i class="ri-flashlight-line me-2 text-muted"></i>Electrical</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_electrical_grade"
                  @change="handleGradeChange('broker_electrical_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_electrical_grade" :class="getGradeBadgeClass(asset.broker_electrical_grade)">
                  {{ asset.broker_electrical_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_electrical_est)"
                  @input="handleCostChange('broker_electrical_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_electrical_est) }}</span>
              </td>
            </tr>
            <tr v-if="asset.broker_landscaping_est || editable">
              <td><i class="ri-plant-line me-2 text-muted"></i>Landscaping</td>
              <td class="text-center">
                <select
                  v-if="editable"
                  :value="asset.broker_landscaping_grade"
                  @change="handleGradeChange('broker_landscaping_grade', $event)"
                  class="form-select form-select-sm"
                >
                  <option :value="null">-</option>
                  <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
                </select>
                <span v-else-if="asset.broker_landscaping_grade" :class="getGradeBadgeClass(asset.broker_landscaping_grade)">
                  {{ asset.broker_landscaping_grade }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <input
                  v-if="editable"
                  type="text"
                  :value="formatEditableCurrency(asset.broker_landscaping_est)"
                  @input="handleCostChange('broker_landscaping_est', $event)"
                  @blur="emitUpdate"
                  class="form-control form-control-sm text-end"
                  placeholder="$0"
                />
                <span v-else>{{ formatCurrency(asset.broker_landscaping_est) }}</span>
              </td>
            </tr>
            <tr v-if="showTotal" class="table-active fw-bold">
              <td><i class="ri-funds-line me-2 text-primary"></i>Total Estimated Rehab</td>
              <td></td>
              <td class="text-end text-primary">{{ formatCurrency(asset.broker_rehab_est) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- WHAT: Empty state if no detailed rehab data (only in read-only mode) -->
    <!-- WHY: In editable mode, always show the table for data entry -->
    <div v-else-if="!editable" class="text-center text-muted py-4">
      <i class="ri-hammer-line display-4 mb-2"></i>
      <p class="mb-0">No detailed rehab breakdown available for this property</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  asset: any
  editable?: boolean
  showHeader?: boolean
  showTotal?: boolean
}>(), {
  editable: false,
  showHeader: true,
  showTotal: true,
})

const emit = defineEmits<{
  (e: 'update', data: Record<string, any>): void
}>()

// WHAT: Grade options
const grades = ['A+', 'A', 'B', 'C', 'D', 'F']

// WHAT: Local data for editable mode
const localData = ref<Record<string, any>>({ ...props.asset })

// WHAT: Watch for asset changes and update local data
// WHY: Keep local data in sync when parent updates
watch(() => props.asset, (newAsset) => {
  if (newAsset) {
    localData.value = { ...newAsset }
  }
}, { deep: true })

// WHAT: Check if asset has any detailed rehab data
function hasDetailedRehab(asset: any): boolean {
  return !!(
    asset.broker_roof_est ||
    asset.broker_kitchen_est ||
    asset.broker_bath_est ||
    asset.broker_flooring_est ||
    asset.broker_windows_est ||
    asset.broker_appliances_est ||
    asset.broker_plumbing_est ||
    asset.broker_electrical_est ||
    asset.broker_landscaping_est
  )
}

// WHAT: Get grade badge class based on grade value
function getGradeBadgeClass(grade: string | null | undefined): string {
  if (!grade) return 'badge bg-secondary'
  
  const gradeUpper = grade.toUpperCase()
  
  switch (gradeUpper) {
    case 'A+':
    case 'A':
      return 'badge bg-success'
    case 'B':
      return 'badge bg-primary'
    case 'C':
      return 'badge bg-warning'
    case 'D':
    case 'F':
      return 'badge bg-danger'
    default:
      return 'badge bg-secondary'
  }
}

// WHAT: Format address from asset
function formatAddress(asset: any): string {
  return asset.street_address || asset.property_address || asset.address || '-'
}

// WHAT: Format city and state
function formatCityState(asset: any): string {
  const city = asset.city || asset.property_city || ''
  const state = asset.state || asset.property_state || ''
  return [city, state].filter(Boolean).join(', ') || '-'
}

// WHAT: Format currency for display (read-only mode)
function formatCurrency(val: number | null | undefined): string {
  if (val == null) return '-'
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD', 
    maximumFractionDigits: 0 
  }).format(val)
}

// WHAT: Format currency for editable input
function formatEditableCurrency(val: number | null | undefined): string {
  if (val == null || val === 0) return ''
  return `$${val.toLocaleString('en-US')}`
}

// WHAT: Handle grade dropdown change
function handleGradeChange(field: string, event: Event) {
  const target = event.target as HTMLSelectElement
  localData.value[field] = target.value || null
  console.log('[DetailedRehabBreakdown] Grade changed:', field, target.value)
  emitUpdate()
}

// WHAT: Handle cost input change
function handleCostChange(field: string, event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value.replace(/[^0-9]/g, '')
  const num = value ? parseInt(value, 10) : null
  localData.value[field] = num
  target.value = num ? `$${num.toLocaleString('en-US')}` : ''
  console.log('[DetailedRehabBreakdown] Cost changed:', field, num)
  // WHAT: Don't emit immediately on input, wait for blur
  // WHY: Avoid too many API calls while user is typing
}

// WHAT: Emit update event with changed data
function emitUpdate() {
  if (props.editable) {
    console.log('[DetailedRehabBreakdown] Emitting update:', localData.value)
    emit('update', localData.value)
  }
}
</script>

<style scoped>
.detailed-rehab-breakdown {
  min-height: 200px;
}

.form-select-sm,
.form-control-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}
</style>

