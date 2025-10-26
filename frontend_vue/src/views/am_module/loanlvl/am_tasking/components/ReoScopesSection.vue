<template>
  <!-- WHAT: Reusable REO scopes section component -->
  <!-- WHY: Display and manage scopes/bids for Trashout and Renovation tasks -->
  <!-- WHERE: Used in ReoCard for task-specific scope management -->
  <div class="mt-3">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h6 class="mb-0 text-muted">Scopes/Bids</h6>
      <button 
        type="button" 
        class="btn btn-sm btn-outline-primary"
        @click="showAddScopeModal = true"
      >
        <i class="fas fa-plus me-1"></i>
        Add Scope
      </button>
    </div>
    
    <!-- Scopes list -->
    <div v-if="scopes.length === 0" class="text-muted small text-center py-2">
      No scopes yet
    </div>
    <div v-else class="scopes-list">
      <div 
        v-for="scope in scopes.filter(s => s && s.id)" 
        :key="scope.id" 
        class="scope-item"
      >
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center flex-wrap gap-2 small ms-2">
            <strong class="text-dark">${{ formatCost(scope.total_cost) }}</strong>
            <span v-if="scope.vendor_firm" class="text-muted">{{ scope.vendor_firm }}</span>
            <span v-if="scope.vendor_contact" class="text-muted">{{ scope.vendor_contact }}</span>
            <span v-if="scope.scope_date" class="text-muted">{{ formatDate(scope.scope_date) }}</span>
            <span v-if="scope.expected_completion" class="text-muted">ETA: {{ formatDate(scope.expected_completion) }}</span>
          </div>
          <div class="dropdown position-relative me-2">
            <button 
              class="btn btn-xs btn-outline-dark scope-menu-btn" 
              type="button" 
              @click="toggleDropdown(scope.id)"
            >
              ⋮
            </button>
            <ul 
              v-if="openDropdownId === scope.id"
              class="dropdown-menu show position-absolute"
              style="right: 0; top: 100%;"
            >
              <li><button class="dropdown-item" type="button" @click="editScope(scope); openDropdownId = null">Edit</button></li>
              <li><button class="dropdown-item text-danger" type="button" @click="deleteScope(scope.id); openDropdownId = null">Delete</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- WHAT: Add/Edit Scope Modal Component -->
    <!-- WHY: Separate component for better code organization -->
    <AddReoScopeModal 
      v-model="showAddScopeModal" 
      :hub-id="hubId" 
      :task-id="taskId"
      :task-type="taskType"
      :editing-scope="editingScope"
      @scope-added="handleScopeAdded"
      @scope-updated="handleScopeUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import http from '@/lib/http'
import AddReoScopeModal from './AddReoScopeModal.vue'

// WHAT: Component props
// WHY: Receive hub ID, task ID, and task type from parent
interface Props {
  hubId: number
  taskId: number
  taskType: 'trashout' | 'renovation'
}

const props = defineProps<Props>()

// WHAT: Scopes data and modal state
// WHY: Manage scopes display and modal interactions
const scopes = ref<any[]>([])
const showAddScopeModal = ref(false)
const openDropdownId = ref<number | null>(null)
const editingScope = ref<any>(null)

// WHAT: Load scopes for this task
// WHY: Display current scopes/bids
async function loadScopes() {
  try {
    const response = await http.get(`/am/outcomes/reo-scopes/?asset_hub_id=${props.hubId}&scope_kind=${props.taskType}&reo_task=${props.taskId}`)
    console.log('Raw scopes response:', response.data)
    
    // Handle both paginated and non-paginated responses
    if (Array.isArray(response.data)) {
      scopes.value = response.data
    } else if (response.data?.results && Array.isArray(response.data.results)) {
      scopes.value = response.data.results
    } else {
      scopes.value = []
    }
    
    console.log('Loaded scopes:', scopes.value)
  } catch (err: any) {
    console.error('Failed to load scopes:', err)
    scopes.value = []
  }
}

// WHAT: Format cost for display
// WHY: Show user-friendly currency format
function formatCost(cost: number | string | null): string {
  if (cost == null) return '0.00'
  const num = typeof cost === 'string' ? parseFloat(cost) : cost
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// WHAT: Format date for display
// WHY: Show user-friendly date format
function formatDate(dateStr: string): string {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

// WHAT: Edit an existing scope
// WHY: Allow modification of scope details
function editScope(scope: any) {
  editingScope.value = { ...scope }
  showAddScopeModal.value = true
}

// WHAT: Delete a scope
// WHY: Remove unwanted or invalid scopes
async function deleteScope(scopeId: number) {
  if (!confirm('Are you sure you want to delete this scope?')) return
  
  try {
    await http.delete(`/am/outcomes/reo-scopes/${scopeId}/`)
    await loadScopes() // Refresh the list
  } catch (err: any) {
    console.error('Failed to delete scope:', err)
    alert('Failed to delete scope. Please try again.')
  }
}

// WHAT: Handle scope added event from modal
// WHY: Refresh scopes list when new scope is created
function handleScopeAdded() {
  editingScope.value = null
  loadScopes()
}

// WHAT: Handle scope updated event from modal
// WHY: Refresh scopes list when scope is updated
function handleScopeUpdated() {
  editingScope.value = null
  loadScopes()
}

// WHAT: Toggle dropdown menu for scope actions
// WHY: Show/hide edit and delete options
function toggleDropdown(scopeId: number) {
  if (openDropdownId.value === scopeId) {
    openDropdownId.value = null
  } else {
    openDropdownId.value = scopeId
  }
}

// WHAT: Handle click outside to close dropdown
// WHY: Improve user experience
function handleDocClick(e: MouseEvent) {
  const target = e.target as Element
  const dropdownButton = target.closest('.dropdown button')
  
  // Close scope action dropdown if clicking outside
  if (openDropdownId.value !== null && !dropdownButton) {
    openDropdownId.value = null
  }
}

// WHAT: Initialize component
// WHY: Load scopes and setup event listeners
onMounted(() => {
  loadScopes()
  document.addEventListener('click', handleDocClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocClick)
})

// WHAT: Expose load function for parent components
// WHY: Allow parent to refresh scopes when needed
defineExpose({
  loadScopes
})
</script>

<style scoped>
/* WHAT: Scope item styling matching offer cards exactly */
/* WHY: Consistent UI across offers and scopes */
.scopes-list {
  background-color: transparent;
  padding: 0.25rem 0.25rem 0.75rem 0.25rem;
}

.scope-item {
  padding: 0.75rem;
  margin: 0.25rem;
  border-bottom: none;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.scope-item:last-child {
  border-bottom: none;
}

.scope-menu-btn {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  line-height: 1;
  min-width: 1.5rem;
  height: 1.5rem;
  border-color: #6c757d;
}

.scope-menu-btn:hover {
  background-color: #f8f9fa;
  border-color: #495057;
}

.btn-xs {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  line-height: 1;
  border-radius: 0.25rem;
}
</style>
