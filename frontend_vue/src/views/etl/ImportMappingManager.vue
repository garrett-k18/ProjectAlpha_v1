<template>
  <Layout>
    <!--
      ImportMappingManager - Edit column mappings for imported trade
      WHAT: UI for reviewing and changing Excel column → database field mappings
      WHY: Users need to correct or adjust mappings after import
      HOW: Show source columns with dropdown to change target field mappings
    -->
    <div class="row">
      <div class="col-12">
        <div class="page-title-box">
          <div class="page-title-right">
            <button class="btn btn-sm btn-secondary" @click="goBackToDashboard">
              <i class="mdi mdi-arrow-left me-1"></i>Back to Dashboard
            </button>
          </div>
          <h4 class="page-title">
            <i class="mdi mdi-map-marker-path me-2"></i>Edit Import Mappings
          </h4>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mt-2">Loading mappings...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="row">
      <div class="col-12">
        <div class="alert alert-danger">
          <i class="mdi mdi-alert-circle me-2"></i>{{ error }}
        </div>
      </div>
    </div>

    <!-- No Trade Selected -->
    <div v-else-if="!tradeId" class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="mdi mdi-alert-circle-outline display-1 text-muted mb-3"></i>
            <h5>No Trade Selected</h5>
            <p class="text-muted mb-3">
              Please select a trade from the dashboard to view and edit its import mappings.
            </p>
            <button class="btn btn-primary" @click="goBackToDashboard">
              <i class="mdi mdi-arrow-left me-1"></i>Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mapping Editor -->
    <div v-else class="row">
      <div class="col-12">
        <!-- Trade Info Card -->
        <div class="card mb-3">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-1">
                  {{ tradeName }}
                  <span v-if="isLegacy" class="badge bg-warning text-dark ms-2">
                    <i class="mdi mdi-alert me-1"></i>Legacy Import
                  </span>
                </h5>
                <p class="text-muted mb-0">{{ recordCount }} records imported</p>
              </div>
              <div>
                <button 
                  v-if="!editMode && !isLegacy" 
                  class="btn btn-primary" 
                  @click="enableEditMode"
                >
                  <i class="mdi mdi-pencil me-1"></i>Edit Mappings
                </button>
                <button 
                  v-else-if="!editMode && isLegacy"
                  class="btn btn-secondary" 
                  disabled
                  title="Legacy imports cannot be edited. Please re-import to enable mapping edits."
                >
                  <i class="mdi mdi-lock me-1"></i>Read Only
                </button>
                <template v-else>
                  <button 
                    class="btn btn-success me-2" 
                    @click="saveChanges"
                    :disabled="saving"
                  >
                    <i class="mdi mdi-content-save me-1"></i>
                    {{ saving ? 'Saving...' : 'Save Changes' }}
                  </button>
                  <button 
                    class="btn btn-secondary" 
                    @click="cancelEdit"
                    :disabled="saving"
                  >
                    <i class="mdi mdi-close me-1"></i>Cancel
                  </button>
                </template>
              </div>
            </div>
          </div>
        </div>

        <!-- Mappings Table -->
        <div class="card">
          <div class="card-header">
            <h4 class="card-title mb-0">
              <i class="mdi mdi-table-edit me-2"></i>
              {{ isLegacy ? 'Field Audit (Read-Only)' : 'Column Mappings' }}
            </h4>
          </div>
          <div class="card-body">
            <!-- Legacy Import Warning -->
            <div v-if="isLegacy" class="alert alert-warning">
              <i class="mdi mdi-alert-circle me-2"></i>
              <strong>Legacy Import:</strong> This trade was imported before mapping storage was implemented. 
              This view shows which database fields contain data, but the original Excel column headers are not available. 
              To enable mapping edits, please re-import the file.
            </div>
            
            <!-- Normal Info -->
            <div v-else class="alert alert-info">
              <i class="mdi mdi-information me-2"></i>
              <strong>How to use:</strong> This shows your original Excel column headers and which database fields they're mapped to.
              {{ editMode ? 'Use the dropdowns to change where each column maps.' : 'Click "Edit Mappings" to make changes.' }}
            </div>

            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead>
                  <tr>
                    <th style="width: 30%;">
                      {{ isLegacy ? 'Database Field' : 'Source Column (Excel)' }}
                    </th>
                    <th v-if="!isLegacy" style="width: 5%;"></th>
                    <th v-if="!isLegacy" style="width: 30%;">Target Field (Database)</th>
                    <th :style="isLegacy ? 'width: 70%;' : 'width: 35%;'">Sample Data</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-if="isLegacy">
                    <!-- Legacy Import View -->
                    <tr v-for="(mapping, index) in mappings" :key="'legacy-' + index">
                      <td>
                        <code class="text-success">{{ mapping.target_field }}</code>
                        <div class="text-muted small">{{ mapping.source_column }}</div>
                      </td>
                      <td>
                        <div v-if="mapping.samples && mapping.samples.length > 0">
                          <span 
                            v-for="(sample, idx) in mapping.samples" 
                            :key="idx"
                            class="badge bg-light text-dark me-1 mb-1"
                          >
                            {{ sample }}
                          </span>
                        </div>
                        <span v-else class="text-muted">—</span>
                      </td>
                    </tr>
                  </template>
                  
                  <template v-else>
                    <!-- Normal Import View -->
                    <tr v-for="(mapping, index) in mappings" :key="'normal-' + index">
                      <td>
                        <code class="text-primary">{{ mapping.source_column }}</code>
                      </td>
                      <td class="text-center">
                        <i class="mdi mdi-arrow-right text-muted"></i>
                      </td>
                      <td>
                        <select 
                          v-if="editMode"
                          v-model="editableMappings[mapping.source_column]"
                          class="form-select form-select-sm"
                        >
                          <option value="">-- Skip / Unmapped --</option>
                          <option 
                            v-for="field in availableFields" 
                            :key="field.name" 
                            :value="field.name"
                          >
                            {{ field.label }} ({{ field.name }})
                          </option>
                        </select>
                        <code v-else class="text-success">
                          {{ mapping.target_field || '(unmapped)' }}
                        </code>
                      </td>
                      <td>
                        <div v-if="mapping.samples && mapping.samples.length > 0">
                          <span 
                            v-for="(sample, idx) in mapping.samples" 
                            :key="idx"
                            class="badge bg-light text-dark me-1 mb-1"
                          >
                            {{ sample }}
                          </span>
                        </div>
                        <span v-else class="text-muted">—</span>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>
            </div>

            <!-- Summary Stats -->
            <div class="row mt-3">
              <div class="col-md-4">
                <div class="card bg-light">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ mappings.length }}</h3>
                    <p class="text-muted mb-0">
                      {{ isLegacy ? 'Populated Fields' : 'Source Columns' }}
                    </p>
                  </div>
                </div>
              </div>
              <div v-if="!isLegacy" class="col-md-4">
                <div class="card bg-success text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ mappedCount }}</h3>
                    <p class="mb-0">Mapped</p>
                  </div>
                </div>
              </div>
              <div v-if="!isLegacy" class="col-md-4">
                <div class="card bg-warning text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ unmappedCount }}</h3>
                    <p class="mb-0">Unmapped</p>
                  </div>
                </div>
              </div>
              <div v-if="isLegacy" class="col-md-4">
                <div class="card bg-info text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">{{ recordCount }}</h3>
                    <p class="mb-0">Records</p>
                  </div>
                </div>
              </div>
              <div v-if="isLegacy" class="col-md-4">
                <div class="card bg-secondary text-white">
                  <div class="card-body text-center py-3">
                    <h3 class="mb-0">Read-Only</h3>
                    <p class="mb-0">Import Mode</p>
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

<script>
import http from '@/lib/http';
import Layout from '@/components/layouts/layout.vue';

export default {
  name: 'ImportMappingManager',
  components: {
    Layout
  },
  data() {
    return {
      // WHAT: Component state
      // WHY: Track trade, mapping data, and edit state
      // HOW: Reactive data properties
      tradeId: null,
      tradeName: '',
      mappingId: null,
      mappings: [],
      availableFields: [],
      editableMappings: {},
      originalMappings: {},
      recordCount: 0,
      loading: false,
      error: null,
      editMode: false,
      saving: false,
      isLegacy: false,
    };
  },
  
  computed: {
    /**
     * WHAT: Count mapped columns
     * WHY: Show summary stat
     * HOW: Filter non-empty mappings
     */
    mappedCount() {
      return Object.values(this.editableMappings).filter(v => v).length;
    },
    
    /**
     * WHAT: Count unmapped columns
     * WHY: Show summary stat
     * HOW: Filter empty mappings
     */
    unmappedCount() {
      return Object.values(this.editableMappings).filter(v => !v).length;
    }
  },
  
  mounted() {
    // WHAT: Get trade ID from route query
    // WHY: Need to know which trade's mapping to load
    // HOW: Check route query params
    this.tradeId = this.$route.query.trade_id;
    
    if (this.tradeId) {
      this.loadMappings();
    }
  },
  
  methods: {
    /**
     * WHAT: Load mappings for current trade
     * WHY: Display mapping data to user
     * HOW: GET request to API
     */
    async loadMappings() {
      this.loading = true;
      this.error = null;
      
      try {
        // WHAT: Fetch mappings from API
        // WHY: Get source columns and their target fields
        // HOW: Call the field-schema endpoint
        const response = await http.get(`/etl/field-schema/${this.tradeId}/`);
        
        this.mappings = response.data.mappings || [];
        this.availableFields = response.data.available_fields || [];
        this.tradeName = response.data.trade_name || '';
        this.recordCount = response.data.record_count || 0;
        this.mappingId = response.data.mapping_id;
        this.isLegacy = response.data.is_legacy || false;
        
        // WHAT: Initialize editable mappings
        // WHY: Need working copy for editing
        // HOW: Build dict from mappings array
        this.editableMappings = {};
        this.mappings.forEach(m => {
          this.editableMappings[m.source_column] = m.target_field;
        });
        this.originalMappings = { ...this.editableMappings };
        
      } catch (error) {
        console.error('Failed to load mappings:', error);
        this.error = error.response?.data?.error || 'Failed to load mappings. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * WHAT: Enable edit mode
     * WHY: Allow user to modify mappings
     * HOW: Set editMode flag
     */
    enableEditMode() {
      this.editMode = true;
    },
    
    /**
     * WHAT: Cancel edit mode
     * WHY: Discard changes
     * HOW: Restore original mappings and disable edit mode
     */
    cancelEdit() {
      this.editableMappings = { ...this.originalMappings };
      this.editMode = false;
    },
    
    /**
     * WHAT: Save mapping changes
     * WHY: Persist user's edits to database
     * HOW: POST request to update mapping
     */
    async saveChanges() {
      this.saving = true;
      
      try {
        // WHAT: Update mapping with new column_mapping
        // WHY: Save user's changes
        // HOW: POST request with updated data
        const response = await http.post(`/etl/field-schema/${this.tradeId}/`, {
          column_mapping: this.editableMappings
        });
        
        // WHAT: Update local state with saved data
        // WHY: Reflect changes in UI
        // HOW: Update originalMappings and reload
        this.originalMappings = { ...this.editableMappings };
        this.editMode = false;
        
        // WHAT: Show success message
        // WHY: Confirm save to user
        alert(response.data.message || 'Mapping saved successfully!');
        
        // WHAT: Reload mappings to get updated sample data
        // WHY: Show current state
        await this.loadMappings();
        
      } catch (error) {
        console.error('Failed to save mappings:', error);
        alert('Failed to save mappings. Please try again.');
      } finally {
        this.saving = false;
      }
    },
    
    /**
     * WHAT: Navigate back to acquisitions dashboard
     * WHY: Return to main workflow
     * HOW: Use Vue Router
     */
    goBackToDashboard() {
      this.$router.push('/acquisitions');
    }
  }
};
</script>

<style scoped>
/* WHAT: Custom styles for mapping editor */
/* WHY: Enhance UI appearance */
/* HOW: Scoped CSS */

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

code {
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #f8f9fa;
}

.card {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}
</style>
