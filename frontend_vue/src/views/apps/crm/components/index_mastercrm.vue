<template>
  <!--
    Master CRM List View Component
    Reusable component for Brokers, Clients, Trading Partners, etc.
    Component path: frontend_vue/src/components/crm/CRMListView.vue
  -->
  <b-row>
    <b-col cols="12">
      <div class="card">
        <div class="card-body">
          <!-- Top Bar: Search, Filters, Actions -->
          <b-row class="mb-2">
            <b-col xl="8">
              <b-form class="row gy-2 gx-2 align-items-center justify-content-xl-start justify-content-between">
                <!-- Search Input -->
                <b-col class="col-auto">
                  <label :for="`search-${entityType}`" class="visually-hidden">Search</label>
                  <input 
                    type="search" 
                    class="form-control" 
                    :id="`search-${entityType}`" 
                    placeholder="Search..."
                    v-model="searchQuery"
                    @input="onSearch"
                  >
                </b-col>

                <!-- Dynamic Filters -->
                <b-col 
                  v-for="filter in filters" 
                  :key="filter.field"
                  class="col-auto"
                >
                  <div class="d-flex align-items-center">
                    <label :for="`${filter.field}-select`" class="me-2">{{ filter.label }}</label>
                    <select 
                      class="form-select" 
                      :id="`${filter.field}-select`"
                      v-model="activeFilters[filter.field]"
                      @change="onFilterChange"
                    >
                      <option value="">All</option>
                      <option 
                        v-for="option in filter.options" 
                        :key="option"
                        :value="option"
                      >
                        {{ option }}
                      </option>
                    </select>
                  </div>
                </b-col>
              </b-form>
            </b-col>

            <!-- Action Buttons -->
            <b-col xl="4">
              <div class="text-xl-end mt-xl-0 mt-2">
                <button 
                  type="button" 
                  class="btn btn-danger mb-2 me-2" 
                  @click="showModal = true"
                >
                  <i class="mdi mdi-account-plus-outline me-1"></i>
                  {{ addButtonText }}
                </button>
                <button type="button" class="btn btn-light mb-2" @click="onExport">
                  Export
                </button>
              </div>
            </b-col>
          </b-row>

          <!-- Add/Edit Modal -->
          <b-modal 
            v-model="showModal" 
            :title="isEditing ? `Edit ${entityType}` : `Add ${entityType}`" 
            hide-footer
            size="lg"
          >
            <b-form @submit.prevent="onSubmit">
              <b-row class="g-2">
                <b-col 
                  v-for="column in editableColumns"
                  :key="column.field"
                  :cols="column.cols || 12"
                  :md="column.md || 6"
                >
                  <label class="form-label">{{ column.header }}</label>
                  <!-- If options provided and multiple, render checkbox group for better UX -->
                  <div v-if="column.options && column.options.length && column.multiple" class="border rounded p-2" style="max-height: 220px; overflow: auto;">
                    <div class="d-flex justify-content-end mb-2 gap-2">
                      <button type="button" class="btn btn-sm btn-light" @click="form[column.field] = column.options.map(o => o.value)">Select all</button>
                      <button type="button" class="btn btn-sm btn-light" @click="form[column.field] = []">Clear</button>
                    </div>
                    <div class="d-flex flex-column gap-1">
                      <div class="form-check" v-for="opt in column.options" :key="opt.value">
                        <input
                          class="form-check-input"
                          type="checkbox"
                          :id="`${column.field}-${opt.value}`"
                          :value="opt.value"
                          v-model="form[column.field]"
                        />
                        <label class="form-check-label" :for="`${column.field}-${opt.value}`">{{ opt.label }}</label>
                      </div>
                    </div>
                  </div>
                  <!-- If options provided (single select), render select -->
                  <select
                    v-else-if="column.options && column.options.length"
                    class="form-select"
                    v-model="form[column.field]"
                  >
                    <option v-for="opt in column.options" :key="opt.value" :value="opt.value">
                      {{ opt.label }}
                    </option>
                  </select>
                  <!-- Fallback: standard input -->
                  <input
                    v-else
                    class="form-control"
                    v-model="form[column.field]"
                    :type="column.inputType || 'text'"
                    :placeholder="column.placeholder || ''"
                    :maxlength="column.maxlength"
                    @input="(e: Event) => column.transform ? form[column.field] = column.transform((e.target as HTMLInputElement).value) : null"
                  />
                  </b-col>
              </b-row>

              <div class="d-flex justify-content-end mt-3">
                <button type="button" class="btn btn-light me-2" @click="onCancel">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  {{ isEditing ? `Update ${entityType}` : `Save ${entityType}` }}
                </button>
              </div>
            </b-form>
          </b-modal>

          <!-- Data Table -->
          <div class="table-responsive">
            <table class="table table-sm table-centered table-nowrap mb-0 crm-table">
              <thead class="table-light">
                <tr>
                  <th style="width: 20px;">
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="selectAll">
                      <label class="form-check-label" for="selectAll">&nbsp;</label>
                    </div>
                  </th>
                  <th v-for="column in tableColumns" :key="column.field" :style="column.width ? `width: ${column.width}` : ''">
                    {{ column.header }}
                  </th>
                  <th style="width: 125px;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <!-- Loading State -->
                <tr v-if="loading">
                  <td :colspan="tableColumns.length + 2">
                    <div class="text-center py-3">Loading {{ entityType }}s…</div>
                  </td>
                </tr>

                <!-- Error State -->
                <tr v-else-if="error">
                  <td :colspan="tableColumns.length + 2">
                    <div class="text-danger">{{ error }}</div>
                  </td>
                </tr>

                <!-- Empty State -->
                <tr v-else-if="!data.length">
                  <td :colspan="tableColumns.length + 2">
                    <div class="text-muted">No {{ entityType }}s found.</div>
                  </td>
                </tr>

                <!-- Data Rows -->
                <tr v-else v-for="row in data" :key="row.id">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" :id="`row-${row.id}`">
                      <label class="form-check-label" :for="`row-${row.id}`">&nbsp;</label>
                    </div>
                  </td>
                  <td v-for="column in tableColumns" :key="column.field">
                    <!-- Custom checkbox rendering for NDA flag -->
                    <div v-if="column.field === 'nda_flag'" class="form-check">
                      <input 
                        type="checkbox" 
                        class="form-check-input" 
                        :id="`nda-${row.id}`"
                        :checked="row.nda_flag"
                        disabled
                      >
                      <label class="form-check-label" :for="`nda-${row.id}`">&nbsp;</label>
                    </div>
                    <!-- Array-as-chips rendering for better readability (e.g., states) -->
                    <div v-else-if="Array.isArray(row[column.field])">
                      <span v-if="row[column.field].length === 0" class="text-muted">—</span>
                      <span v-else>
                        <span
                          v-for="(val, idx) in row[column.field]"
                          :key="idx + '-' + val"
                          class="badge bg-light text-dark border me-1"
                        >
                          {{ val }}
                        </span>
                      </span>
                    </div>
                    <!-- Standard cell rendering -->
                    <component 
                      v-else
                      :is="column.component || 'span'" 
                      v-bind="column.componentProps ? column.componentProps(row) : {}"
                    >
                      {{ column.formatter ? column.formatter(row) : (row[column.field] || '—') }}
                    </component>
                  </td>
                  <td>
                    <!-- View NDA action (only for trading partners with NDA) -->
                    <a 
                      v-if="row.nda_flag && entityType === 'Trading Partner'" 
                      href="javascript:void(0);" 
                      class="action-icon me-2" 
                      title="View NDA" 
                      @click="$emit('view-nda', row)"
                    >
                      <i class="mdi mdi-file-document-outline"></i>
                    </a>
                    <!-- Edit action -->
                    <a href="javascript:void(0);" class="action-icon" title="Edit" @click="onEdit(row)">
                      <i class="mdi mdi-square-edit-outline"></i>
                    </a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { PropType } from 'vue';

/**
 * Column configuration interface
 */
export interface CRMColumn {
  field: string;              // Data field name
  header: string;             // Column header text
  width?: string;             // Optional column width
  editable?: boolean;         // Show in edit modal
  inputType?: string;         // Input type for modal (text, email, tel, etc.)
  placeholder?: string;       // Placeholder for input
  maxlength?: number;         // Max length for input
  transform?: (val: any) => any;  // Transform function for input
  formatter?: (row: any) => string;  // Custom formatter for display
  component?: string;         // Custom component for cell
  componentProps?: (row: any) => any;  // Props for custom component
  cols?: number;              // Bootstrap cols for modal
  md?: number;                // Bootstrap md cols for modal
  // Optional: select options for this field in the modal; if provided, a select is rendered
  options?: Array<{ value: string; label: string }>;
  // Optional: when using select, allow multiple selection
  multiple?: boolean;
}

/**
 * Filter configuration interface
 */
export interface CRMFilter {
  field: string;              // Field to filter on
  label: string;              // Filter label
  options: string[];          // Filter options
}

export default defineComponent({
  name: 'CRMListView',

  props: {
    // Entity type (e.g., "Broker", "Client", "Trading Partner")
    entityType: {
      type: String,
      required: true,
    },

    // Column configuration
    columns: {
      type: Array as PropType<CRMColumn[]>,
      required: true,
    },

    // Filters configuration
    filters: {
      type: Array as PropType<CRMFilter[]>,
      default: () => [],
    },
    addButtonText: {
      type: String,
      default: 'Add New',
    },

    // Data array
    data: {
      type: Array as PropType<any[]>,
      default: () => [],
    },

    // Loading state
    loading: {
      type: Boolean,
      default: false,
    },

    // Error message
    error: {
      type: String as PropType<string | null>,
      default: null,
    },
  },

  emits: ['search', 'filter', 'create', 'update', 'export', 'view-nda'],

  data() {
    return {
      showModal: false,
      isEditing: false,
      editId: null as number | null,
      form: {} as Record<string, any>,
      submitting: false,
      searchQuery: '',
      activeFilters: {} as Record<string, string>,
    };
  },

  computed: {
    /**
     * Columns to show in table
     */
    tableColumns(): CRMColumn[] {
      return this.columns;
    },

    /**
     * Columns to show in edit modal
     */
    editableColumns(): CRMColumn[] {
      return this.columns.filter((col: CRMColumn) => col.editable !== false);
    },
  },

  methods: {
    /**
     * Handle search input
     */
    onSearch() {
      this.$emit('search', this.searchQuery);
    },

    /**
     * Handle filter change
     */
    onFilterChange() {
      this.$emit('filter', this.activeFilters);
    },

    /**
     * Handle export
     */
    onExport() {
      this.$emit('export');
    },

    /**
     * Reset form to initial state
     */
    resetForm() {
      this.form = {};
      this.editableColumns.forEach(col => {
        // Initialize array for multi-select fields, else empty string
        this.form[col.field] = col.multiple ? [] : '';
      });
    },

    /**
     * Handle cancel from modal
     */
    onCancel() {
      this.resetForm();
      this.showModal = false;
      this.isEditing = false;
      this.editId = null;
    },

    /**
     * Handle form submit (create or update)
     */
    async onSubmit() {
      this.submitting = true;

      if (this.isEditing && this.editId != null) {
        this.$emit('update', { id: this.editId, data: this.form });
      } else {
        this.$emit('create', this.form);
      }

      // Parent component should handle the actual API call and close modal
      // For now, we'll close after a short delay
      setTimeout(() => {
        this.submitting = false;
        this.showModal = false;
        this.resetForm();
        this.isEditing = false;
        this.editId = null;
      }, 500);
    },

    /**
     * Populate form and open modal in editing mode
     */
    onEdit(row: any) {
      this.isEditing = true;
      this.editId = row.id;
      
      this.editableColumns.forEach(col => {
        // Preserve arrays when multi-select, else map to string value
        if (col.multiple) {
          this.form[col.field] = Array.isArray(row[col.field]) ? [...row[col.field]] : [];
        } else {
          this.form[col.field] = row[col.field] || '';
        }
      });

      this.showModal = true;
    },
  },

  mounted() {
    this.resetForm();
  },
});
</script>

<style scoped>
/* Keep row height compact */
.crm-table td,
.crm-table th {
  padding-top: 0.35rem;
  padding-bottom: 0.35rem;
  vertical-align: middle;
}
</style>
