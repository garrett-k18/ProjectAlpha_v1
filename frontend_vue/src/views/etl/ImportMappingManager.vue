<template>
  <!--
    ImportMappingManager - Review and edit column mappings for data imports
    WHAT: UI for managing saved import column mappings
    WHY: Users need to review, edit, and reuse successful mappings
    HOW: List/detail view with mapping editor and validation
  -->
  <div class="import-mapping-manager">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
              <h4 class="card-title mb-0">
                <i class="mdi mdi-map-marker-path me-2"></i>Import Column Mappings
              </h4>
              <button class="btn btn-primary btn-sm" @click="showCreateModal">
                <i class="mdi mdi-plus me-1"></i>New Mapping
              </button>
            </div>
          </div>

          <div class="card-body">
            <!-- Filters -->
            <div class="row mb-3">
              <div class="col-md-4">
                <label class="form-label">Filter by Seller</label>
                <select v-model="filters.seller" class="form-select" @change="loadMappings">
                  <option value="">All Sellers</option>
                  <option v-for="seller in sellers" :key="seller.id" :value="seller.id">
                    {{ seller.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Status</label>
                <select v-model="filters.is_active" class="form-select" @change="loadMappings">
                  <option value="">All</option>
                  <option value="true">Active</option>
                  <option value="false">Archived</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label">Search</label>
                <input
                  v-model="filters.search"
                  type="text"
                  class="form-control"
                  placeholder="Search mappings..."
                  @input="debouncedSearch"
                />
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="text-muted mt-2">Loading mappings...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="alert alert-danger">
              <i class="mdi mdi-alert-circle me-2"></i>{{ error }}
            </div>

            <!-- Empty State -->
            <div v-else-if="mappings.length === 0" class="text-center py-5">
              <i class="mdi mdi-map-marker-off display-3 text-muted mb-3"></i>
              <h5>No Mappings Found</h5>
              <p class="text-muted">Create a new mapping or adjust your filters.</p>
            </div>

            <!-- Mappings List -->
            <div v-else class="table-responsive">
              <table class="table table-hover align-middle">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Seller</th>
                    <th>Method</th>
                    <th>Fields</th>
                    <th>Status</th>
                    <th>Last Used</th>
                    <th>Usage</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="mapping in mappings" :key="mapping.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <i
                          class="mdi mdi-star me-2"
                          :class="mapping.is_default ? 'text-warning' : 'text-muted'"
                          :title="mapping.is_default ? 'Default mapping' : ''"
                        ></i>
                        <div>
                          <div class="fw-semibold">{{ mapping.mapping_name }}</div>
                          <small v-if="mapping.original_filename" class="text-muted">
                            {{ mapping.original_filename }}
                          </small>
                        </div>
                      </div>
                    </td>
                    <td>{{ mapping.seller_name || 'N/A' }}</td>
                    <td>
                      <span class="badge" :class="getMethodBadgeClass(mapping.mapping_method)">
                        {{ mapping.mapping_method }}
                      </span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ mapping.mapped_field_count }} fields</span>
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="mapping.is_active ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ mapping.is_active ? 'Active' : 'Archived' }}
                      </span>
                      <i
                        v-if="!mapping.is_valid_mapping"
                        class="mdi mdi-alert-circle text-danger ms-1"
                        title="Mapping validation failed"
                      ></i>
                    </td>
                    <td>
                      <small v-if="mapping.last_used_at">
                        {{ formatDate(mapping.last_used_at) }}
                      </small>
                      <small v-else class="text-muted">Never</small>
                    </td>
                    <td>{{ mapping.usage_count }}x</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          @click="viewMapping(mapping)"
                          title="View Details"
                        >
                          <i class="mdi mdi-eye"></i>
                        </button>
                        <button
                          class="btn btn-outline-secondary"
                          @click="editMapping(mapping)"
                          title="Edit Mapping"
                        >
                          <i class="mdi mdi-pencil"></i>
                        </button>
                        <button
                          class="btn btn-outline-info"
                          @click="duplicateMapping(mapping)"
                          title="Duplicate"
                        >
                          <i class="mdi mdi-content-copy"></i>
                        </button>
                        <button
                          v-if="mapping.is_active"
                          class="btn btn-outline-warning"
                          @click="archiveMapping(mapping)"
                          title="Archive"
                        >
                          <i class="mdi mdi-archive"></i>
                        </button>
                        <button
                          v-else
                          class="btn btn-outline-success"
                          @click="restoreMapping(mapping)"
                          title="Restore"
                        >
                          <i class="mdi mdi-restore"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mapping Detail/Edit Modal -->
    <div
      v-if="selectedMapping"
      class="modal fade show d-block"
      tabindex="-1"
      style="background-color: rgba(0, 0, 0, 0.5)"
      @click.self="closeModal"
    >
      <div class="modal-dialog modal-xl modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="mdi mdi-map-marker-path me-2"></i>
              {{ editMode ? 'Edit' : 'View' }} Mapping: {{ selectedMapping.mapping_name }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>

          <div class="modal-body">
            <!-- Mapping Info -->
            <div class="row mb-4">
              <div class="col-md-6">
                <label class="form-label">Mapping Name</label>
                <input
                  v-model="selectedMapping.mapping_name"
                  type="text"
                  class="form-control"
                  :readonly="!editMode"
                />
              </div>
              <div class="col-md-6">
                <label class="form-label">Method</label>
                <input
                  :value="selectedMapping.mapping_method"
                  type="text"
                  class="form-control"
                  readonly
                />
              </div>
              <div class="col-12 mt-3">
                <label class="form-label">Notes</label>
                <textarea
                  v-model="selectedMapping.notes"
                  class="form-control"
                  rows="2"
                  :readonly="!editMode"
                ></textarea>
              </div>
            </div>

            <!-- Mapping Settings -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="form-check">
                  <input
                    v-model="selectedMapping.is_default"
                    class="form-check-input"
                    type="checkbox"
                    id="isDefaultCheck"
                    :disabled="!editMode"
                  />
                  <label class="form-check-label" for="isDefaultCheck">
                    Set as default for this seller
                  </label>
                </div>
              </div>
              <div class="col-md-6">
                <div class="form-check">
                  <input
                    v-model="selectedMapping.is_active"
                    class="form-check-input"
                    type="checkbox"
                    id="isActiveCheck"
                    :disabled="!editMode"
                  />
                  <label class="form-check-label" for="isActiveCheck">
                    Active
                  </label>
                </div>
              </div>
            </div>

            <!-- Validation Results -->
            <div v-if="selectedMapping.validation_results" class="alert" :class="selectedMapping.validation_results.valid ? 'alert-success' : 'alert-warning'" role="alert">
              <h6 class="alert-heading">
                <i class="mdi" :class="selectedMapping.validation_results.valid ? 'mdi-check-circle' : 'mdi-alert-circle'"></i>
                Validation {{ selectedMapping.validation_results.valid ? 'Passed' : 'Issues Found' }}
              </h6>
              <p class="mb-0">
                Mapped {{ selectedMapping.validation_results.mapped_count }} of {{ selectedMapping.validation_results.valid_fields_count }} available fields
              </p>
              <ul v-if="selectedMapping.validation_results.errors.length > 0" class="mb-0 mt-2">
                <li v-for="(error, index) in selectedMapping.validation_results.errors" :key="index">
                  {{ error }}
                </li>
              </ul>
            </div>

            <!-- Column Mappings Table -->
            <h6 class="mb-3">Column Mappings</h6>
            <div class="table-responsive">
              <table class="table table-sm table-bordered">
                <thead>
                  <tr>
                    <th style="width: 45%">Source Column</th>
                    <th style="width: 45%">Target Field</th>
                    <th v-if="editMode" style="width: 10%">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(targetField, sourceCol) in selectedMapping.column_mapping" :key="sourceCol">
                    <td>
                      <code>{{ sourceCol }}</code>
                    </td>
                    <td>
                      <select
                        v-if="editMode"
                        v-model="selectedMapping.column_mapping[sourceCol]"
                        class="form-select form-select-sm"
                      >
                        <option value="">-- Unmapped --</option>
                        <option
                          v-for="field in availableFields"
                          :key="field.name"
                          :value="field.name"
                        >
                          {{ field.name }} ({{ field.type }})
                        </option>
                      </select>
                      <code v-else>{{ targetField }}</code>
                    </td>
                    <td v-if="editMode">
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="removeMapping(sourceCol)"
                        title="Remove mapping"
                      >
                        <i class="mdi mdi-close"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Unmapped Columns -->
            <div v-if="selectedMapping.unmapped_columns && selectedMapping.unmapped_columns.length > 0" class="mt-3">
              <h6 class="text-muted">Unmapped Source Columns</h6>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="col in selectedMapping.unmapped_columns"
                  :key="col"
                  class="badge bg-secondary"
                >
                  {{ col }}
                </span>
              </div>
            </div>

            <!-- Import Stats -->
            <div v-if="selectedMapping.import_stats && Object.keys(selectedMapping.import_stats).length > 0" class="mt-4">
              <h6>Import Statistics</h6>
              <div class="row g-3">
                <div class="col-md-3" v-if="selectedMapping.import_stats.records_imported">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h4 class="mb-0">{{ selectedMapping.import_stats.records_imported }}</h4>
                      <small class="text-muted">Records Imported</small>
                    </div>
                  </div>
                </div>
                <div class="col-md-3" v-if="selectedMapping.import_stats.records_created">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h4 class="mb-0 text-success">{{ selectedMapping.import_stats.records_created }}</h4>
                      <small class="text-muted">Created</small>
                    </div>
                  </div>
                </div>
                <div class="col-md-3" v-if="selectedMapping.import_stats.records_updated">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h4 class="mb-0 text-info">{{ selectedMapping.import_stats.records_updated }}</h4>
                      <small class="text-muted">Updated</small>
                    </div>
                  </div>
                </div>
                <div class="col-md-3" v-if="selectedMapping.import_stats.errors">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h4 class="mb-0 text-danger">{{ selectedMapping.import_stats.errors }}</h4>
                      <small class="text-muted">Errors</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              {{ editMode ? 'Cancel' : 'Close' }}
            </button>
            <button
              v-if="!editMode"
              type="button"
              class="btn btn-primary"
              @click="editMode = true"
            >
              <i class="mdi mdi-pencil me-1"></i>Edit Mapping
            </button>
            <button
              v-if="editMode"
              type="button"
              class="btn btn-primary"
              @click="saveMapping"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="mdi mdi-content-save me-1"></i>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ImportMappingManager',
  data() {
    return {
      // List state
      mappings: [],
      sellers: [],
      loading: false,
      error: null,
      
      // Filters
      filters: {
        seller: '',
        is_active: 'true', // Show active by default
        search: ''
      },
      
      // Modal state
      selectedMapping: null,
      editMode: false,
      saving: false,
      availableFields: [],
      
      // Debounce timer
      searchTimeout: null
    };
  },
  
  mounted() {
    this.loadSellers();
    this.loadMappings();
  },
  
  methods: {
    /**
     * WHAT: Load list of sellers for filter dropdown
     * WHY: Users need to filter mappings by seller
     * HOW: GET request to sellers API
     */
    async loadSellers() {
      try {
        const response = await axios.get('/api/acq/sellers/');
        this.sellers = response.data;
      } catch (error) {
        console.error('Failed to load sellers:', error);
      }
    },
    
    /**
     * WHAT: Load mappings list with current filters
     * WHY: Display available mappings to user
     * HOW: GET request with query params for filters
     */
    async loadMappings() {
      this.loading = true;
      this.error = null;
      
      try {
        const params = {};
        if (this.filters.seller) params.seller = this.filters.seller;
        if (this.filters.is_active) params.is_active = this.filters.is_active;
        if (this.filters.search) params.search = this.filters.search;
        
        const response = await axios.get('/api/etl/import-mappings/', { params });
        this.mappings = response.data;
      } catch (error) {
        console.error('Failed to load mappings:', error);
        this.error = 'Failed to load mappings. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * WHAT: Debounced search handler
     * WHY: Avoid excessive API calls while typing
     * HOW: Clear previous timeout and set new one
     */
    debouncedSearch() {
      if (this.searchTimeout) clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.loadMappings();
      }, 500);
    },
    
    /**
     * WHAT: View mapping details
     * WHY: Show full mapping configuration
     * HOW: Load detailed mapping data and show modal
     */
    async viewMapping(mapping) {
      try {
        const response = await axios.get(`/api/etl/import-mappings/${mapping.id}/`);
        this.selectedMapping = response.data;
        this.availableFields = response.data.available_target_fields || [];
        this.editMode = false;
      } catch (error) {
        console.error('Failed to load mapping details:', error);
        alert('Failed to load mapping details');
      }
    },
    
    /**
     * WHAT: Edit mapping
     * WHY: Allow users to modify mapping configuration
     * HOW: Load mapping and enable edit mode
     */
    async editMapping(mapping) {
      await this.viewMapping(mapping);
      this.editMode = true;
    },
    
    /**
     * WHAT: Save mapping changes
     * WHY: Persist user edits to database
     * HOW: PUT request with updated mapping data
     */
    async saveMapping() {
      this.saving = true;
      
      try {
        const response = await axios.put(
          `/api/etl/import-mappings/${this.selectedMapping.id}/`,
          this.selectedMapping
        );
        
        // Update mapping in list
        const index = this.mappings.findIndex(m => m.id === this.selectedMapping.id);
        if (index !== -1) {
          this.mappings[index] = { ...this.mappings[index], ...response.data };
        }
        
        this.selectedMapping = response.data;
        this.editMode = false;
        
        // Show success message
        this.$toast?.success('Mapping saved successfully');
      } catch (error) {
        console.error('Failed to save mapping:', error);
        alert('Failed to save mapping. Please try again.');
      } finally {
        this.saving = false;
      }
    },
    
    /**
     * WHAT: Duplicate mapping
     * WHY: Create copy of existing mapping for variations
     * HOW: POST request to duplicate endpoint
     */
    async duplicateMapping(mapping) {
      const newName = prompt('Enter name for duplicated mapping:', `${mapping.mapping_name} (Copy)`);
      if (!newName) return;
      
      try {
        const response = await axios.post(
          `/api/etl/import-mappings/${mapping.id}/duplicate/`,
          { mapping_name: newName }
        );
        
        this.mappings.unshift(response.data);
        this.$toast?.success('Mapping duplicated successfully');
      } catch (error) {
        console.error('Failed to duplicate mapping:', error);
        alert('Failed to duplicate mapping');
      }
    },
    
    /**
     * WHAT: Archive mapping
     * WHY: Hide old mappings without deleting
     * HOW: POST request to archive endpoint
     */
    async archiveMapping(mapping) {
      if (!confirm('Archive this mapping? It can be restored later.')) return;
      
      try {
        await axios.post(`/api/etl/import-mappings/${mapping.id}/archive/`);
        mapping.is_active = false;
        this.$toast?.success('Mapping archived');
      } catch (error) {
        console.error('Failed to archive mapping:', error);
        alert('Failed to archive mapping');
      }
    },
    
    /**
     * WHAT: Restore archived mapping
     * WHY: Reactivate previously archived mapping
     * HOW: POST request to restore endpoint
     */
    async restoreMapping(mapping) {
      try {
        await axios.post(`/api/etl/import-mappings/${mapping.id}/restore/`);
        mapping.is_active = true;
        this.$toast?.success('Mapping restored');
      } catch (error) {
        console.error('Failed to restore mapping:', error);
        alert('Failed to restore mapping');
      }
    },
    
    /**
     * WHAT: Remove a column mapping
     * WHY: Allow users to unmap columns
     * HOW: Delete key from column_mapping object
     */
    removeMapping(sourceCol) {
      if (confirm(`Remove mapping for "${sourceCol}"?`)) {
        delete this.selectedMapping.column_mapping[sourceCol];
        // Force reactivity
        this.selectedMapping.column_mapping = { ...this.selectedMapping.column_mapping };
      }
    },
    
    /**
     * WHAT: Close modal
     * WHY: Exit detail/edit view
     * HOW: Clear selected mapping
     */
    closeModal() {
      this.selectedMapping = null;
      this.editMode = false;
    },
    
    /**
     * WHAT: Show create mapping modal
     * WHY: Allow manual mapping creation
     * HOW: Navigate to creation view (to be implemented)
     */
    showCreateModal() {
      alert('Manual mapping creation coming soon. Mappings are auto-created during imports.');
    },
    
    /**
     * WHAT: Get badge class for mapping method
     * WHY: Visual distinction between mapping methods
     * HOW: Return Bootstrap badge class based on method
     */
    getMethodBadgeClass(method) {
      const classes = {
        'AI': 'bg-primary',
        'MANUAL': 'bg-secondary',
        'EXACT': 'bg-info',
        'HYBRID': 'bg-success'
      };
      return classes[method] || 'bg-secondary';
    },
    
    /**
     * WHAT: Format date for display
     * WHY: Show human-readable dates
     * HOW: Use toLocaleDateString
     */
    formatDate(dateString) {
      if (!dateString) return 'Never';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    /**
     * WHAT: Format file size
     * WHY: Show human-readable file sizes
     * HOW: Convert bytes to KB/MB
     */
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
  }
};
</script>

<style scoped>
/* WHAT: Custom styles for mapping manager */
/* WHY: Enhance UI appearance and usability */
/* HOW: Scoped CSS for component-specific styling */

.import-mapping-manager {
  padding: 20px;
}

.table th {
  font-weight: 600;
  background-color: #f8f9fa;
}

.modal.show {
  display: block;
}

.form-check-input:disabled {
  opacity: 0.5;
}

code {
  background-color: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

.badge {
  font-weight: 500;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
}
</style>
