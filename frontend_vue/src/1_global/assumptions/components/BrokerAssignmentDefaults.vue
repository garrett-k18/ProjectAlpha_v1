<template>
  <!--
    BrokerAssignmentDefaults.vue
    - Component for managing default broker assignment rules and preferences
    - Allows configuration of automatic broker assignment based on various criteria
    - Emits 'changed' event when data is modified
    
    Location: frontend_vue/src/1_global/assumptions/components/BrokerAssignmentDefaults.vue
  -->
  <div class="broker-assignment-defaults">
    <!-- Header Section -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h5 class="mb-1">
          <i class="mdi mdi-account-tie-outline me-2 text-primary"></i>
          Broker Assignment Defaults
        </h5>
        <p class="text-muted mb-0 small">
          Configure default rules for automatic broker assignment to assets
        </p>
      </div>
      <button 
        class="btn btn-sm btn-primary"
        @click="addNewRule"
        :disabled="isLoading"
      >
        <i class="mdi mdi-plus me-1"></i>
        Add Rule
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="text-muted mt-3">Loading broker assignment rules...</p>
    </div>

    <!-- Content Section -->
    <div v-else>
      <!-- Assignment Rules Table -->
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover table-bordered mb-0">
              <thead class="table-light">
                <tr>
                  <th style="width: 5%">#</th>
                  <th style="width: 10%">Priority</th>
                  <th style="width: 30%">MSA (Metropolitan Statistical Area)</th>
                  <th style="width: 10%">State</th>
                  <th style="width: 30%">Default Broker</th>
                  <th style="width: 10%">Active</th>
                  <th style="width: 5%">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="rules.length === 0">
                  <td colspan="7" class="text-center text-muted py-4">
                    <i class="mdi mdi-information-outline me-2"></i>
                    No broker assignment rules configured. Click "Add Rule" to create your first MSA-based assignment rule.
                  </td>
                </tr>
                <tr v-for="(rule, index) in rules" :key="rule.id">
                  <td class="text-center">{{ index + 1 }}</td>
                  <td>
                    <input 
                      v-model.number="rule.priority"
                      type="number"
                      class="form-control form-control-sm"
                      min="1"
                      @change="markChanged"
                    />
                  </td>
                  <td>
                    <select 
                      v-model="rule.msa"
                      class="form-select form-select-sm"
                      @change="markChanged"
                    >
                      <option value="">All MSAs</option>
                      <option v-for="msa in msaOptions" :key="msa.code" :value="msa.code">
                        {{ msa.name }}
                      </option>
                    </select>
                  </td>
                  <td class="text-center">
                    <span v-if="getStatefromMSA(rule.msa)" class="badge bg-secondary">
                      {{ getStatefromMSA(rule.msa) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <select 
                      v-model="rule.brokerId"
                      class="form-select form-select-sm"
                      @change="markChanged"
                    >
                      <option value="">Select Broker...</option>
                      <option v-for="broker in brokerOptions" :key="broker.id" :value="broker.id">
                        {{ broker.name }}
                      </option>
                    </select>
                  </td>
                  <td class="text-center">
                    <div class="form-check form-switch d-flex justify-content-center">
                      <input 
                        v-model="rule.isActive"
                        class="form-check-input"
                        type="checkbox"
                        @change="markChanged"
                      />
                    </div>
                  </td>
                  <td class="text-center">
                    <button 
                      class="btn btn-sm btn-link text-danger p-0"
                      @click="deleteRule(rule.id)"
                      title="Delete Rule"
                    >
                      <i class="mdi mdi-delete-outline"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Info Alert -->
      <div class="alert alert-info mt-3">
        <i class="mdi mdi-information-outline me-2"></i>
        <strong>Note:</strong> Brokers are assigned based on MSA (Metropolitan Statistical Area) for more targeted local market expertise. 
        Rules are evaluated in priority order (lowest number = highest priority).
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * BrokerAssignmentDefaults.vue
 * 
 * What this does:
 * - Manages default broker assignment rules for automatic asset-to-broker matching
 * - Allows configuration of priority-based rules by state, asset type, etc.
 * - Provides settings for auto-assignment behavior and conflict resolution
 * 
 * How it works:
 * - Rules are stored with priority, criteria, and target broker
 * - Emits 'changed' event when any rule or setting is modified
 * - Future: Will integrate with backend API for persistent storage
 * 
 * Events:
 * - changed: Emitted when any data is modified
 */
import { ref, onMounted } from 'vue'

// Define the emit for parent component
const emit = defineEmits<{
  changed: []
}>()

// WHAT: Interface for MSA broker assignment rule
// WHY: Define structure for MSA-based broker assignments
interface AssignmentRule {
  id: number
  priority: number
  msa: string // MSA code
  brokerId: string | number
  isActive: boolean
}

// WHAT: Interface for MSA reference data
// WHY: Store MSA code, name, and state mapping
interface MSAOption {
  code: string
  name: string
  state: string
}

// Loading state
const isLoading = ref<boolean>(false)

// Assignment rules data
const rules = ref<AssignmentRule[]>([])

// WHAT: MSA (Metropolitan Statistical Area) options with codes
// WHY: Major MSAs for broker assignment targeting
// HOW: Sorted by population/importance, covering major markets across US
const msaOptions = ref<MSAOption[]>([
  // Top 25 MSAs by population
  { code: '35620', name: 'New York-Newark-Jersey City, NY-NJ-PA', state: 'NY' },
  { code: '31080', name: 'Los Angeles-Long Beach-Anaheim, CA', state: 'CA' },
  { code: '16980', name: 'Chicago-Naperville-Elgin, IL-IN-WI', state: 'IL' },
  { code: '19100', name: 'Dallas-Fort Worth-Arlington, TX', state: 'TX' },
  { code: '26420', name: 'Houston-The Woodlands-Sugar Land, TX', state: 'TX' },
  { code: '47900', name: 'Washington-Arlington-Alexandria, DC-VA-MD-WV', state: 'DC' },
  { code: '37980', name: 'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD', state: 'PA' },
  { code: '33100', name: 'Miami-Fort Lauderdale-Pompano Beach, FL', state: 'FL' },
  { code: '12060', name: 'Atlanta-Sandy Springs-Alpharetta, GA', state: 'GA' },
  { code: '38060', name: 'Phoenix-Mesa-Chandler, AZ', state: 'AZ' },
  { code: '14460', name: 'Boston-Cambridge-Newton, MA-NH', state: 'MA' },
  { code: '40140', name: 'Riverside-San Bernardino-Ontario, CA', state: 'CA' },
  { code: '19820', name: 'Detroit-Warren-Dearborn, MI', state: 'MI' },
  { code: '42660', name: 'Seattle-Tacoma-Bellevue, WA', state: 'WA' },
  { code: '33460', name: 'Minneapolis-St. Paul-Bloomington, MN-WI', state: 'MN' },
  { code: '41860', name: 'San Francisco-Oakland-Berkeley, CA', state: 'CA' },
  { code: '41740', name: 'San Diego-Chula Vista-Carlsbad, CA', state: 'CA' },
  { code: '45300', name: 'Tampa-St. Petersburg-Clearwater, FL', state: 'FL' },
  { code: '19740', name: 'Denver-Aurora-Lakewood, CO', state: 'CO' },
  { code: '41180', name: 'St. Louis, MO-IL', state: 'MO' },
  { code: '12580', name: 'Baltimore-Columbia-Towson, MD', state: 'MD' },
  { code: '17460', name: 'Cleveland-Elyria, OH', state: 'OH' },
  { code: '36740', name: 'Orlando-Kissimmee-Sanford, FL', state: 'FL' },
  { code: '40900', name: 'Sacramento-Roseville-Folsom, CA', state: 'CA' },
  { code: '38900', name: 'Portland-Vancouver-Hillsboro, OR-WA', state: 'OR' },
  { code: '41700', name: 'San Antonio-New Braunfels, TX', state: 'TX' },
  { code: '32820', name: 'Memphis, TN-MS-AR', state: 'TN' },
  { code: '27260', name: 'Jacksonville, FL', state: 'FL' },
  { code: '28140', name: 'Kansas City, MO-KS', state: 'MO' },
  { code: '17140', name: 'Cincinnati, OH-KY-IN', state: 'OH' },
  { code: '18140', name: 'Columbus, OH', state: 'OH' },
  { code: '29820', name: 'Las Vegas-Henderson-Paradise, NV', state: 'NV' },
  { code: '15380', name: 'Buffalo-Cheektowaga, NY', state: 'NY' },
  { code: '39580', name: 'Raleigh-Cary, NC', state: 'NC' },
  { code: '46060', name: 'Tucson, AZ', state: 'AZ' },
  { code: '26900', name: 'Indianapolis-Carmel-Anderson, IN', state: 'IN' },
  { code: '34980', name: 'Nashville-Davidson-Murfreesboro-Franklin, TN', state: 'TN' },
  { code: '38300', name: 'Pittsburgh, PA', state: 'PA' },
  { code: '17820', name: 'Colorado Springs, CO', state: 'CO' },
  { code: '13820', name: 'Birmingham-Hoover, AL', state: 'AL' },
  { code: '40380', name: 'Rochester, NY', state: 'NY' },
  { code: '16740', name: 'Charlotte-Concord-Gastonia, NC-SC', state: 'NC' },
  { code: '41940', name: 'San Jose-Sunnyvale-Santa Clara, CA', state: 'CA' },
  { code: '36420', name: 'Oklahoma City, OK', state: 'OK' },
  { code: '29460', name: 'Lakeland-Winter Haven, FL', state: 'FL' },
  { code: '35380', name: 'New Orleans-Metairie, LA', state: 'LA' },
  { code: '39300', name: 'Providence-Warwick, RI-MA', state: 'RI' },
  { code: '25540', name: 'Hartford-East Hartford-Middletown, CT', state: 'CT' },
  { code: '40060', name: 'Richmond, VA', state: 'VA' },
  { code: '31140', name: 'Louisville/Jefferson County, KY-IN', state: 'KY' },
])

// Broker options (will be fetched from API in future)
const brokerOptions = ref<{ id: number | string; name: string }[]>([
  { id: 1, name: 'John Smith - California Markets' },
  { id: 2, name: 'Jane Doe - Texas Markets' },
  { id: 3, name: 'Mike Johnson - Florida Markets' },
  { id: 4, name: 'Sarah Williams - Northeast Markets' },
  { id: 5, name: 'Chris Brown - National Coverage' }
])

// Counter for new rule IDs
let nextRuleId = 1

/**
 * WHAT: Mark that changes have been made
 * WHY: Notify parent component to enable save button
 */
function markChanged() {
  emit('changed')
}

/**
 * WHAT: Add a new MSA-based assignment rule
 * WHY: Allow users to create new broker assignment rules by MSA
 */
function addNewRule() {
  const newRule: AssignmentRule = {
    id: nextRuleId++,
    priority: rules.value.length + 1,
    msa: '',
    brokerId: '',
    isActive: true
  }
  rules.value.push(newRule)
  markChanged()
}

/**
 * WHAT: Get state code from MSA code
 * WHY: Display which state an MSA belongs to
 * @param msaCode - The MSA code to look up
 * @returns State abbreviation or empty string if not found
 */
function getStatefromMSA(msaCode: string): string {
  if (!msaCode) return ''
  const msa = msaOptions.value.find(m => m.code === msaCode)
  return msa ? msa.state : ''
}

/**
 * WHAT: Delete an assignment rule
 * WHY: Allow users to remove unnecessary rules
 * @param ruleId - The ID of the rule to delete
 */
function deleteRule(ruleId: number) {
  const index = rules.value.findIndex(r => r.id === ruleId)
  if (index !== -1) {
    rules.value.splice(index, 1)
    markChanged()
  }
}

/**
 * WHAT: Load existing rules and settings from API
 * WHY: Populate the form with existing configuration
 * TODO: Implement actual API integration
 */
async function loadData() {
  isLoading.value = true
  try {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // TODO: Replace with actual API call
    // const response = await http.get('/api/broker-assignment-defaults/')
    // rules.value = response.data.rules
    // settings.value = response.data.settings
    
    // For now, initialize with empty data
    rules.value = []
    
    console.log('Broker assignment defaults loaded')
  } catch (error) {
    console.error('Error loading broker assignment defaults:', error)
  } finally {
    isLoading.value = false
  }
}

// Load data on component mount
onMounted(() => {
  loadData()
})
</script>

<style scoped>
/**
 * Styling for broker assignment defaults component
 * Uses Bootstrap/Hyper UI utilities with minimal custom CSS
 */
.broker-assignment-defaults {
  /* Component wrapper styles */
}

.form-control-sm,
.form-select-sm {
  font-size: 0.875rem;
}

.form-check-input {
  cursor: pointer;
}

.table th {
  font-weight: 600;
  color: #313a46;
  background-color: #f1f3fa;
}

.table td {
  vertical-align: middle;
}

.btn-link {
  text-decoration: none;
}

.btn-link:hover {
  text-decoration: none;
}

/* Responsive table adjustments */
@media (max-width: 767.98px) {
  .table-responsive {
    font-size: 0.875rem;
  }
}
</style>

