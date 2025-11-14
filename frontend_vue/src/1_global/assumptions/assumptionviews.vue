<template>
  <!--
    AssumptionViews.vue
    - Central hub for viewing and editing reference tables and assumptions
    - Organized into tabs: State Assumptions, Foreclosure Timelines, etc.
    - Users can view and modify modeling assumptions across the platform
    
    Location: frontend_vue/src/1_global/assumptionviews.vue
  -->
  <Layout>
    <Breadcrumb :items="breadcrumbItems" :title="pageTitle" />

    <div class="row">
      <div class="col-12">
        <!-- Page Header Card -->
        <div class="card mb-3">
          <div class="card-body py-3">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h4 class="header-title mb-1">
                  <i class="mdi mdi-table-cog me-2"></i>Reference Tables & Assumptions
                </h4>
                <p class="text-muted mb-0">View and edit modeling assumptions and reference data</p>
              </div>
              <div>
                <button 
                  class="btn btn-sm btn-success"
                  @click="saveAllChanges"
                  :disabled="!hasUnsavedChanges || isSaving"
                >
                  <i class="mdi mdi-content-save me-1"></i>
                  {{ isSaving ? 'Saving...' : 'Save All Changes' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content with Sidebar Layout -->
        <div class="card">
          <div class="card-body p-0">
            <div class="row g-0">
              <!-- Sidebar Navigation -->
              <div class="col-md-3 col-lg-2 border-end">
                <div class="sidebar-nav">
                  <div class="nav flex-column" role="tablist">
                    <!-- State Assumptions -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'state-assumptions' }"
                      href="#"
                      @click.prevent="activeTab = 'state-assumptions'"
                      role="tab"
                    >
                      <i class="mdi mdi-map-marker-outline me-2"></i>
                      <span>State Assumptions</span>
                    </a>
                    
                    <!-- Foreclosure Timelines -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'foreclosure-timelines' }"
                      href="#"
                      @click.prevent="activeTab = 'foreclosure-timelines'"
                      role="tab"
                    >
                      <i class="mdi mdi-clock-outline me-2"></i>
                      <span>Foreclosure Timelines</span>
                    </a>
                    
                    <!-- MSA Assumptions -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'msa-assumptions' }"
                      href="#"
                      @click.prevent="activeTab = 'msa-assumptions'"
                      role="tab"
                    >
                      <i class="mdi mdi-city-variant-outline me-2"></i>
                      <span>MSA Assumptions</span>
                    </a>
                    
                    <!-- Modeling Assumptions -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'modeling-assumptions' }"
                      href="#"
                      @click.prevent="activeTab = 'modeling-assumptions'"
                      role="tab"
                    >
                      <i class="mdi mdi-tune-variant me-2"></i>
                      <span>Modeling Assumptions</span>
                    </a>
                    
                    <!-- Commercial Asset Assumptions -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'commercial-asset-assumptions' }"
                      href="#"
                      @click.prevent="activeTab = 'commercial-asset-assumptions'"
                      role="tab"
                    >
                      <i class="mdi mdi-office-building-cog-outline me-2"></i>
                      <span>Commercial Asset Assumptions</span>
                    </a>
                    
                    <!-- Servicer Assumptions -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'servicer-assumptions' }"
                      href="#"
                      @click.prevent="activeTab = 'servicer-assumptions'"
                      role="tab"
                    >
                      <i class="mdi mdi-account-cog-outline me-2"></i>
                      <span>Servicer Assumptions</span>
                    </a>
                    
                    <!-- Broker Assignment Defaults -->
                    <a 
                      class="nav-link"
                      :class="{ active: activeTab === 'broker-assignment-defaults' }"
                      href="#"
                      @click.prevent="activeTab = 'broker-assignment-defaults'"
                      role="tab"
                    >
                      <i class="mdi mdi-account-tie-outline me-2"></i>
                      <span>Broker Assignment Defaults</span>
                    </a>
                  </div>
                </div>
              </div>

              <!-- Content Area -->
              <div class="col-md-9 col-lg-10">
                <div class="tab-content p-4">
                  <!-- State Assumptions Tab -->
                  <div 
                    v-show="activeTab === 'state-assumptions'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'state-assumptions' }"
                    role="tabpanel"
                  >
                    <StateAssumptionsTable 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- Foreclosure Timelines Tab -->
                  <div 
                    v-show="activeTab === 'foreclosure-timelines'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'foreclosure-timelines' }"
                    role="tabpanel"
                  >
                    <ForeclosureTimelinesTable 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- MSA Assumptions Tab -->
                  <div 
                    v-show="activeTab === 'msa-assumptions'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'msa-assumptions' }"
                    role="tabpanel"
                  >
                    <MsaAssumptionsTable 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- Modeling Assumptions Tab -->
                  <div 
                    v-show="activeTab === 'modeling-assumptions'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'modeling-assumptions' }"
                    role="tabpanel"
                  >
                    <ModelingAssumptions 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- Commercial Asset Assumptions Tab -->
                  <div 
                    v-show="activeTab === 'commercial-asset-assumptions'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'commercial-asset-assumptions' }"
                    role="tabpanel"
                  >
                    <CommercialAssetAssumptions 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- Servicer Assumptions Tab -->
                  <div 
                    v-show="activeTab === 'servicer-assumptions'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'servicer-assumptions' }"
                    role="tabpanel"
                  >
                    <ServicerAssumptions 
                      @changed="markAsChanged"
                    />
                  </div>

                  <!-- Broker Assignment Defaults Tab -->
                  <div 
                    v-show="activeTab === 'broker-assignment-defaults'"
                    class="tab-pane"
                    :class="{ active: activeTab === 'broker-assignment-defaults' }"
                    role="tabpanel"
                  >
                    <BrokerAssignmentDefaults 
                      @changed="markAsChanged"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
/**
 * AssumptionViews.vue
 * 
 * What this does:
 * - Provides a centralized interface for managing reference tables and assumptions
 * - Organizes different assumption types into tabs for easy navigation
 * - Tracks unsaved changes and provides a unified save mechanism
 * 
 * How it works:
 * - Each tab contains a dedicated component for a specific assumption type
 * - Child components emit 'changed' events when data is modified
 * - Save All button triggers save across all modified tabs
 * 
 * Components used:
 * - StateAssumptionsTable: State-level assumptions (14+ editable fields: timelines, rates, costs, etc.)
 * - ForeclosureTimelinesTable: Foreclosure timeline assumptions by state
 */
import { ref } from 'vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import Layout from '@/components/layouts/layout.vue'
import StateAssumptionsTable from './components/StateAssumptionsTable.vue'
import ForeclosureTimelinesTable from './components/ForeclosureTimelinesTable.vue'
import MsaAssumptionsTable from './components/MsaAssumptionsTable.vue'
import ModelingAssumptions from './components/ModelingAssumptions.vue'
import CommercialAssetAssumptions from './components/CommercialAssetAssumptions.vue'
import ServicerAssumptions from './components/ServicerAssumptions.vue'
import BrokerAssignmentDefaults from './components/BrokerAssignmentDefaults.vue'

// Page metadata
const pageTitle = ref('Assumptions & Reference Tables')
const breadcrumbItems = ref([
  {
    text: 'Home',
    href: '/',
  },
  {
    text: 'Settings',
    href: '#',
  },
  {
    text: 'Assumptions',
    active: true,
  },
])

// Tab state
const activeTab = ref<
  'state-assumptions' |
  'foreclosure-timelines' |
  'msa-assumptions' |
  'modeling-assumptions' |
  'commercial-asset-assumptions' |
  'servicer-assumptions' |
  'broker-assignment-defaults'
>('state-assumptions')

// Change tracking
const hasUnsavedChanges = ref(false)
const isSaving = ref(false)

/**
 * Mark that changes have been made in any tab
 * Called by child components when data is modified
 */
function markAsChanged() {
  hasUnsavedChanges.value = true
}

/**
 * Save all pending changes across all tabs
 * Triggers save in all child components
 */
async function saveAllChanges() {
  isSaving.value = true
  try {
    // TODO: Implement save logic - emit event to child components
    // or call their save methods directly via refs
    console.log('Saving all changes...')
    
    // Simulate save delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    hasUnsavedChanges.value = false
  } catch (error) {
    console.error('Error saving changes:', error)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
/**
 * Styling for the assumptions management page with sidebar navigation
 * Uses Bootstrap/Hyper UI utilities with minimal custom CSS
 */

/* Sidebar Navigation Styles */
.sidebar-nav {
  min-height: 600px;
  background-color: #fafbfe;
}

.sidebar-nav .nav {
  padding: 0;
}

.sidebar-nav .nav-link {
  display: flex;
  align-items: center;
  padding: 1rem 1.25rem;
  color: #6c757d;
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
}

.sidebar-nav .nav-link:hover {
  background-color: #f1f3fa;
  color: #313a46;
}

.sidebar-nav .nav-link.active {
  background-color: #fff;
  color: #3577f1;
  border-left-color: #3577f1;
  font-weight: 600;
}

.sidebar-nav .nav-link i {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.sidebar-nav .nav-link span {
  flex: 1;
}

/* Border styling */
.border-end {
  border-right: 1px solid #e3eaef !important;
}

/* Tab Content Area */
.tab-content {
  min-height: 600px;
}

/* Responsive adjustments */
@media (max-width: 767.98px) {
  .sidebar-nav {
    min-height: auto;
    border-bottom: 1px solid #e3eaef;
  }
  
  .sidebar-nav .nav {
    flex-direction: row !important;
    overflow-x: auto;
  }
  
  .sidebar-nav .nav-link {
    white-space: nowrap;
    border-left: none;
    border-bottom: 3px solid transparent;
  }
  
  .sidebar-nav .nav-link.active {
    border-left: none;
    border-bottom-color: #3577f1;
  }
  
  .tab-content {
    padding: 1rem !important;
  }
}
</style>
