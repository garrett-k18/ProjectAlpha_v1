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
        <div class="card">
          <div class="card-body" style="padding-bottom: 2rem;">
            <!-- Page Header -->
            <div class="d-flex justify-content-between align-items-center mb-3">
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

            <!-- Tab Navigation -->
            <ul class="nav nav-tabs nav-bordered mb-3" role="tablist">
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'state-assumptions' }"
                  href="#"
                  @click.prevent="activeTab = 'state-assumptions'"
                  role="tab"
                >
                  <i class="mdi mdi-map-marker-outline me-1"></i>
                  State Assumptions
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'foreclosure-timelines' }"
                  href="#"
                  @click.prevent="activeTab = 'foreclosure-timelines'"
                  role="tab"
                >
                  <i class="mdi mdi-clock-outline me-1"></i>
                  Foreclosure Timelines
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'msa-assumptions' }"
                  href="#"
                  @click.prevent="activeTab = 'msa-assumptions'"
                  role="tab"
                >
                  <i class="mdi mdi-city-variant-outline me-1"></i>
                  MSA Assumptions
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'modeling-assumptions' }"
                  href="#"
                  @click.prevent="activeTab = 'modeling-assumptions'"
                  role="tab"
                >
                  <i class="mdi mdi-tune-variant me-1"></i>
                  Modeling Assumptions
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'commercial-asset-assumptions' }"
                  href="#"
                  @click.prevent="activeTab = 'commercial-asset-assumptions'"
                  role="tab"
                >
                  <i class="mdi mdi-office-building-cog-outline me-1"></i>
                  Commercial Asset Assumptions
                </a>
              </li>
              <li class="nav-item" role="presentation">
                <a 
                  class="nav-link"
                  :class="{ active: activeTab === 'servicer-assumptions' }"
                  href="#"
                  @click.prevent="activeTab = 'servicer-assumptions'"
                  role="tab"
                >
                  <i class="mdi mdi-account-cog-outline me-1"></i>
                  Servicer Assumptions
                </a>
              </li>
            </ul>

            <!-- Tab Content -->
            <div class="tab-content">
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
  'servicer-assumptions'
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
 * Styling for the assumptions management page
 * Uses Bootstrap/Hyper UI utilities with minimal custom CSS
 */
.nav-tabs .nav-link {
  cursor: pointer;
}

.nav-tabs .nav-link:hover {
  background-color: #f1f3fa;
}
</style>
