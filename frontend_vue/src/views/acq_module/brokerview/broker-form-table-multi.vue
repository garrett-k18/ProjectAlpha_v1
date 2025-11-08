<template>
  <!--
    BrokerFormTableMulti - Refactored to match OverviewTab.vue style
    
    WHAT: Modern, filterable valuation table for broker portal
    WHY: Consistent UI/UX with internal valuation center
    HOW: Styled like OverviewTab.vue with filters, pagination, and clean layout
    
    Columns:
      - Loan # (from sellertape_id if available)
      - Address (street, city, state)
      - Quick Links (Zillow, Redfin, Realtor)
      - As-Is Value (editable)
      - ARV Value (editable)
      - Estimated Rehab (editable)
      - Notes (modal)
      - Photos (upload + viewer)
      - Documents (upload)
      - Links (add URLs)
      - Status (auto-save indicator)
  -->
  <div>
    <!-- WHAT: Advanced Filters Section (matching OverviewTab.vue) -->
    <!-- WHY: Allow brokers to filter their assigned properties by multiple criteria -->
    <div class="card bg-light border mb-3">
      <div class="card-body py-3">
        <div class="row g-2 align-items-end">
          <!-- Search Box (Address or Loan Number) -->
          <div class="col-md-3">
            <label class="form-label small mb-1">Search</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control form-control-sm" 
              placeholder="Search by address or loan number..."
              @input="applyFilters"
            />
          </div>
          
          <!-- State Filter -->
          <div class="col-md-2">
            <label class="form-label small mb-1">State</label>
            <select 
              v-model="filters.state" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="">All States</option>
              <option v-for="state in availableStates" :key="state" :value="state">
                {{ state }}
              </option>
            </select>
          </div>
          
          <!-- Grade Filter -->
          <div class="col-md-1">
            <label class="form-label small mb-1">Grade</label>
            <select 
              v-model="filters.grade" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="">All</option>
              <option value="none">None</option>
              <option value="A+">A+</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="F">F</option>
            </select>
          </div>
          
          <!-- Value Source Selector -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Value Filter</label>
            <select 
              v-model="filters.valueSource" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value="asis">As-Is</option>
              <option value="arv">ARV</option>
            </select>
          </div>
          
          <!-- Value Operator -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Operator</label>
            <select 
              v-model="filters.valueOperator" 
              class="form-select form-select-sm"
              @change="applyFilters"
            >
              <option value=">">Greater Than</option>
              <option value="<">Less Than</option>
              <option value="=">Equal To</option>
              <option value=">=">Greater or Equal</option>
              <option value="<=">Less or Equal</option>
            </select>
          </div>
          
          <!-- Value Filter -->
          <div class="col-md-2">
            <label class="form-label small mb-1">Amount</label>
            <input 
              type="text" 
              class="form-control form-control-sm" 
              :value="formatNumberWithCommas(filters.valueAmount)"
              @input="handleValueFilterInput"
              placeholder="Enter amount"
            />
          </div>
          
          <!-- Clear Filters Button -->
          <div class="col-md-1">
            <button 
              class="btn btn-sm btn-light w-100" 
              @click="clearFilters"
              title="Clear all filters"
            >
              <i class="ri-filter-off-line"></i>
            </button>
          </div>
        </div>
        
        <!-- Filter Results Count -->
        <div class="mt-2 small text-muted">
          Showing {{ paginatedRows.length }} of {{ filteredRows.length }} properties
          <span v-if="filteredRows.length < normalizedRows.length">
            (filtered from {{ normalizedRows.length }} total)
          </span>
        </div>
      </div>
    </div>
    
    <!-- WHAT: Main Valuation Table -->
    <!-- WHY: Display assigned properties in clean, modern format -->
    <div class="table-responsive">
      <table class="table table-centered table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Loan #</th>
            <th>Address</th>
            <th class="text-center">Grade</th>
            <th class="text-center">As-Is Value</th>
            <th class="text-center">ARV Value</th>
            <th class="text-center">Est. Rehab</th>
            <th class="text-center">Notes</th>
            <th class="text-center">Attachments</th>
            <th class="text-center">Inspection</th>
            <th class="text-center">Links</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!filteredRows || filteredRows.length === 0">
            <td colspan="10" class="text-center text-muted py-3">
              <span v-if="filters.search || filters.state || filters.valueAmount || filters.grade">
                No properties match your filters
              </span>
              <span v-else>
                No active assignments are available at this time
              </span>
            </td>
          </tr>
          <tr v-for="(entry, idx) in paginatedRows" :key="entry.key">
            <!-- WHAT: Loan Number Column -->
            <!-- WHY: Primary identifier for the property -->
            <td>
              <div class="fw-semibold">
                {{ getLoanNumber(entry) || '-' }}
              </div>
            </td>
            
            <!-- WHAT: Address Column (matching OverviewTab.vue style) -->
            <!-- WHY: Clean display with street and city/state on separate lines -->
            <td>
              <div class="fw-semibold">
                {{ getStreetAddress(entry) }}
              </div>
              <div class="small text-muted">
                {{ getCityState(entry) }}
              </div>
            </td>
            
            <!-- WHAT: Grade Column (editable dropdown) -->
            <!-- WHY: Allow brokers to assign grades to properties they're evaluating -->
            <td class="text-center">
              <select 
                class="form-select form-select-sm grade-select"
                :value="getGrade(getActualIndex(entry))"
                @change="(e) => handleSaveGrade(getActualIndex(entry), (e.target as HTMLSelectElement).value)"
                :disabled="!entry.inviteToken"
              >
                <option value="">-</option>
                <option value="A+">A+</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
                <option value="F">F</option>
              </select>
            </td>

            <!-- WHAT: As-Is Value - Editable inline input (matching OverviewTab.vue style) -->
            <!-- WHY: Clean, minimal input without input-group wrapper -->
            <td class="text-center">
              <input
                type="text"
                class="editable-value-inline"
                v-model="asIsInput[getActualIndex(entry)]"
                @input="handleCurrencyInput(getActualIndex(entry), 'asIs', $event)"
                @blur="scheduleAutoSave(getActualIndex(entry))"
                @keyup.enter="scheduleAutoSave(getActualIndex(entry))"
                placeholder="Add Value"
                :disabled="!entry.inviteToken || photoUploadStatus[getActualIndex(entry)] === 'uploading'"
              />
            </td>

            <!-- WHAT: ARV Value - Editable inline input -->
            <!-- WHY: Consistent styling with As-Is Value -->
            <td class="text-center">
              <input
                type="text"
                class="editable-value-inline"
                v-model="arvInput[getActualIndex(entry)]"
                @input="handleCurrencyInput(getActualIndex(entry), 'arv', $event)"
                @blur="scheduleAutoSave(getActualIndex(entry))"
                @keyup.enter="scheduleAutoSave(getActualIndex(entry))"
                placeholder="Add Value"
                :disabled="!entry.inviteToken || photoUploadStatus[getActualIndex(entry)] === 'uploading'"
              />
            </td>

            <!-- WHAT: Estimated Rehab - Editable inline input -->
            <!-- WHY: Consistent styling with other value inputs -->
            <td class="text-center">
              <input
                type="text"
                class="editable-value-inline"
                v-model="rehabInput[getActualIndex(entry)]"
                @input="handleCurrencyInput(getActualIndex(entry), 'rehab', $event)"
                @blur="scheduleAutoSave(getActualIndex(entry))"
                @keyup.enter="scheduleAutoSave(getActualIndex(entry))"
                placeholder="Add Value"
                :disabled="!entry.inviteToken || photoUploadStatus[getActualIndex(entry)] === 'uploading'"
              />
            </td>

            <!-- WHAT: Notes - Multi-line text preview with edit icon at end -->
            <!-- WHY: Show note preview (up to 2 lines) with clear edit indicator -->
            <td class="text-center">
              <div 
                class="notes-preview-container" 
                @click="openNotes(getActualIndex(entry))"
                :title="rowsState[getActualIndex(entry)]?.notes || 'Click to add note'"
              >
                <div v-if="rowsState[getActualIndex(entry)]?.notes" class="notes-with-icon">
                  <span class="notes-text-multiline">
                    {{ truncateText(rowsState[getActualIndex(entry)].notes, 60) }}
                  </span>
                  <i class="ri-edit-line notes-edit-icon"></i>
                </div>
                <div v-else class="notes-placeholder">
                  <i class="ri-file-text-line"></i> Add Note
                </div>
              </div>
              <!-- Notes modal per row -->
              <b-modal
                v-model="notesOpen[getActualIndex(entry)]"
                title="Valuation Note"
                ok-title="Save"
                cancel-title="Cancel"
                @ok="onSaveNotes(getActualIndex(entry))"
              >
                <b-form-textarea
                  v-model="rowsState[getActualIndex(entry)].notes"
                  rows="6"
                  placeholder="Enter detailed notes here..."
                />
              </b-modal>
            </td>

            <!-- WHAT: Attachments - Unified upload manager for photos and documents -->
            <!-- WHY: Cleaner UX with single button opening modal for all file types -->
            <td class="text-center">
              <button
                class="btn btn-sm btn-light"
                @click="openAttachmentsModal(getActualIndex(entry))"
                :disabled="!entry.inviteToken"
                :title="getAttachmentsSummary(getActualIndex(entry))"
              >
                <i class="ri-attachment-2"></i>
                <span v-if="getTotalAttachments(getActualIndex(entry)) > 0" class="badge bg-info ms-1">
                  {{ getTotalAttachments(getActualIndex(entry)) }}
                </span>
              </button>
              
              <!-- WHAT: Attachments modal - unified upload manager -->
              <!-- WHY: Single place to manage all file uploads (photos and documents) -->
              <b-modal
                v-model="attachmentsModalOpen[getActualIndex(entry)]"
                title="Property Attachments"
                ok-only
                ok-title="Close"
                size="xl"
              >
                <div class="p-3">
                  <!-- WHAT: Photos Section -->
                  <div class="mb-4">
                    <h6 class="d-flex align-items-center mb-3">
                      <i class="ri-image-line me-2"></i>
                      Photos
                      <span v-if="photoThumbs[getActualIndex(entry)]?.length" class="badge bg-info ms-2">
                        {{ photoThumbs[getActualIndex(entry)].length }}
                      </span>
                    </h6>
                    
                    <!-- Photo Upload Controls -->
                    <div class="mb-3">
                      <input
                        class="form-control"
                        type="file"
                        accept="image/*"
                        multiple
                        @change="onPhotoSelected(getActualIndex(entry), $event)"
                        :disabled="photoUploadStatus[getActualIndex(entry)] === 'uploading'"
                      />
                      <div v-if="photoUploadStatus[getActualIndex(entry)] === 'uploading'" class="mt-2">
                        <div class="progress" style="height: 6px;">
                          <div 
                            class="progress-bar" 
                            :style="{ width: photoUploadProgress[getActualIndex(entry)] + '%' }"
                          ></div>
                        </div>
                        <small class="text-muted">Uploading {{ photoUploadProgress[getActualIndex(entry)] }}%</small>
                      </div>
                      <small v-else-if="photoUploadStatus[getActualIndex(entry)] === 'uploaded'" class="text-success d-block mt-1">
                        <i class="ri-check-line"></i> Photos uploaded successfully
                      </small>
                    </div>
                    
                    <!-- Photo Gallery -->
                    <div v-if="photoThumbs[getActualIndex(entry)]?.length" class="row g-2">
                      <div v-for="(p, j) in photoThumbs[getActualIndex(entry)]" :key="j" class="col-3">
                        <a
                          :href="p.src"
                          target="_blank"
                          rel="noopener"
                          class="d-block position-relative"
                        >
                          <img 
                            :src="p.thumb || p.src" 
                            :alt="p.alt || 'Photo'" 
                            class="img-fluid rounded" 
                            style="width: 100%; height: 120px; object-fit: cover;" 
                          />
                        </a>
                      </div>
                    </div>
                    <div v-else class="text-center text-muted py-3 border rounded">
                      <i class="ri-image-line" style="font-size: 2rem; opacity: 0.5;"></i>
                      <p class="mb-0 small">No photos uploaded yet</p>
                    </div>
                  </div>
                  
                  <!-- WHAT: Documents Section -->
                  <div class="mb-2">
                    <h6 class="d-flex align-items-center mb-3">
                      <i class="ri-file-text-line me-2"></i>
                      Documents
                      <span v-if="rowsState[getActualIndex(entry)]?.docFiles?.length" class="badge bg-info ms-2">
                        {{ rowsState[getActualIndex(entry)].docFiles.length }}
                      </span>
                    </h6>
                    
                    <!-- Document Upload Controls -->
                    <div class="mb-3">
                      <input
                        class="form-control"
                        type="file"
                        multiple
                        @change="onDocsSelected(getActualIndex(entry), $event)"
                        :disabled="photoUploadStatus[getActualIndex(entry)] === 'uploading'"
                      />
                      <small v-if="rowsState[getActualIndex(entry)]?.docFiles?.length" class="text-muted d-block mt-1">
                        {{ rowsState[getActualIndex(entry)].docFiles.length }} document(s) selected
                      </small>
                    </div>
                    
                    <!-- Document List (placeholder - can be enhanced later) -->
                    <div class="text-center text-muted py-3 border rounded">
                      <i class="ri-file-list-line" style="font-size: 2rem; opacity: 0.5;"></i>
                      <p class="mb-0 small">Document management coming soon</p>
                    </div>
                  </div>
                </div>
              </b-modal>
            </td>

            <!-- WHAT: Inspection Report - Opens condition assessment modal -->
            <!-- WHY: Allow broker to view/edit repair grades and costs -->
            <td class="text-center">
              <button 
                class="btn btn-sm btn-outline-primary"
                @click="openInspectionModal(getActualIndex(entry))"
                :disabled="!entry.inviteToken"
                title="View Inspection Report"
              >
                <i class="ri-file-list-3-line"></i>
              </button>
              
              <!-- Inspection Report Modal -->
              <b-modal
                v-model="inspectionModalOpen[getActualIndex(entry)]"
                :title="`Detailed Rehab Breakdown - ${getLoanNumber(entry)}`"
                size="lg"
                ok-only
                ok-title="Close"
              >
                <DetailedRehabBreakdown 
                  :asset="{ ...entry, ...entry.prefillValues }" 
                  :editable="true"
                  :showHeader="true"
                  :showTotal="true"
                  @update="handleRehabUpdate(getActualIndex(entry), $event)"
                />
              </b-modal>
            </td>

            <!-- WHAT: Links - Shows hyperlinks or input to add -->
            <!-- WHY: Clean display - input only when adding, otherwise just blue links -->
            <td class="text-center">
              <div class="links-cell">
                <!-- WHAT: Display saved links (truncated if too long) -->
                <div v-if="rowsState[getActualIndex(entry)]?.links?.length" class="saved-links-list mb-1">
                  <div v-for="(lnk, j) in rowsState[getActualIndex(entry)].links" :key="j" class="saved-link-item">
                    <a :href="lnk" target="_blank" rel="noopener" class="link-truncated" :title="lnk">
                      {{ truncateText(lnk, 35) }}
                    </a>
                    <button 
                      class="btn-link-remove" 
                      @click="removeLink(getActualIndex(entry), j)"
                      title="Remove link"
                    >
                      <i class="ri-close-line"></i>
                    </button>
                  </div>
                </div>
                
                <!-- WHAT: Show "Add Link" text or input field -->
                <div v-if="!linkInputVisible[getActualIndex(entry)]" class="text-center">
                  <span 
                    v-if="entry.inviteToken"
                    class="add-link-text"
                    @click="showLinkInput(getActualIndex(entry))"
                  >
                    Add Link
                  </span>
                </div>
                <input
                  v-else
                  ref="linkInputRefs"
                  v-model="linkInput[getActualIndex(entry)]"
                  type="url"
                  class="form-control form-control-sm"
                  placeholder="Paste link..."
                  @blur="addLinkOnBlur(getActualIndex(entry))"
                  @keyup.enter="addLinkOnBlur(getActualIndex(entry))"
                  @keyup.escape="hideLinkInput(getActualIndex(entry))"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- WHAT: Pagination Controls (matching OverviewTab.vue) -->
    <!-- WHY: Handle large numbers of properties gracefully -->
    <div class="d-flex justify-content-between align-items-center mt-3">
      <div class="text-muted small">
        Page {{ currentPage }} of {{ totalPages }}
      </div>
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage - 1)">Previous</a>
          </li>
          <li 
            class="page-item" 
            v-for="page in visiblePages" 
            :key="page"
            :class="{ active: page === currentPage }"
          >
            <a class="page-link" href="#" @click.prevent="goToPage(page)">{{ page }}</a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="goToPage(currentPage + 1)">Next</a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch, onMounted } from 'vue'
import type { PropType } from 'vue'
import axios from 'axios'
import type { AxiosProgressEvent } from 'axios'
import DetailedRehabBreakdown from '@/components/property_tabs_components/DetailedRehabBreakdown.vue'

// WHAT: Row entry provided by parent. Normalized structure used by this component.
// WHY: Type-safe interface for broker portal table rows
// HOW: Extends with loan_number field from hub-first backend refactor
export interface BrokerFormEntry {
  key: string // unique key per row (e.g., `${srdId}:${token}`)
  srdId: number | null
  inviteToken: string | null // null when not active; component disables saving
  address: string
  loan_number?: string | null  // WHAT: Actual loan number from sellertape_id (added in hub-first refactor)
  prefillValues: {
    broker_asis_value?: string | number | null
    broker_arv_value?: string | number | null
    broker_rehab_est?: string | number | null
    broker_value_date?: string | null
    broker_notes?: string | null
    broker_grade?: string | null  // WHAT: Broker quality grade (A+, A, B, C, D, F)
    broker_links?: string | null
    // WHAT: Detailed rehab breakdown fields
    // WHY: Support inspection report modal with trade-by-trade estimates
    broker_roof_grade?: string | null
    broker_roof_est?: number | null
    broker_kitchen_grade?: string | null
    broker_kitchen_est?: number | null
    broker_bath_grade?: string | null
    broker_bath_est?: number | null
    broker_flooring_grade?: string | null
    broker_flooring_est?: number | null
    broker_windows_grade?: string | null
    broker_windows_est?: number | null
    broker_appliances_grade?: string | null
    broker_appliances_est?: number | null
    broker_plumbing_grade?: string | null
    broker_plumbing_est?: number | null
    broker_electrical_grade?: string | null
    broker_electrical_est?: number | null
    broker_landscaping_grade?: string | null
    broker_landscaping_est?: number | null
  } | null
}

// Normalized photo item returned by `/api/acq/photos/<srdId>/`
// src: absolute URL to the image
// alt: alternative text provided by backend (may default for broker photos)
// thumb: optional thumbnail URL (falls back to src)
// type: classification tag such as 'broker', 'public', 'document'
type OutputPhotoItem = { src: string; alt?: string; thumb?: string; type?: string }

export default defineComponent({
  name: 'BrokerFormTableMulti',
  components: {
    DetailedRehabBreakdown,
  },
  props: {
    // v-model support for parent (kept for compatibility)
    modelValue: {
      type: Object as () => { [key: string]: any },
      required: true,
    },
    // Array of normalized entries to render as rows
    rows: {
      type: Array as PropType<BrokerFormEntry[]>,
      default: () => [],
    },
  },
  emits: ['update:modelValue', 'saved'],
  setup(props, { emit }) {
    // WHAT: Reactive per-row state for valuation inputs
    // WHY: Track data per property for auto-save functionality
    const rowsState = ref(
      props.rows.map(() => ({
        asIs: undefined as number | undefined,
        arv: undefined as number | undefined,
        rehab: undefined as number | undefined,
        notes: '' as string,
        photoFiles: [] as File[],
        docFiles: [] as File[],
        links: [] as string[],
      }))
    )

    // WHAT: UI helpers per row (modals and inputs)
    // WHY: Track open/closed state for each row's modals
    const notesOpen = ref<boolean[]>(props.rows.map(() => false))
    const attachmentsModalOpen = ref<boolean[]>(props.rows.map(() => false))
    const inspectionModalOpen = ref<boolean[]>(props.rows.map(() => false))
    const linksModalOpen = ref<boolean[]>(props.rows.map(() => false))
    const linkInputVisible = ref<boolean[]>(props.rows.map(() => false))
    const linkInput = ref<string[]>(props.rows.map(() => ''))
    const asIsInput = ref<string[]>(props.rows.map(() => ''))
    const arvInput = ref<string[]>(props.rows.map(() => ''))
    const rehabInput = ref<string[]>(props.rows.map(() => ''))
    // Per-row photo viewer modal open state
    const photoViewerOpen = ref<boolean[]>(props.rows.map(() => false))

    // Per-row save state
    const isSaving = ref<boolean[]>(props.rows.map(() => false))
    const saveMessage = ref<string[]>(props.rows.map(() => ''))
    const autoSaveStatus = ref<Array<'idle' | 'saving' | 'saved' | 'error'>>(
      props.rows.map(() => 'idle')
    )

    // Per-row photo upload UI state
    // photoUploadStatus: tracks current upload state for each row
    // photoUploadMessage: captures last success/error message for each row
    // photoUploadProgress: 0-100 integer progress for active upload
    const photoUploadStatus = ref<Array<'idle' | 'uploading' | 'uploaded' | 'error'>>(
      props.rows.map(() => 'idle')
    )
    const photoUploadMessage = ref<string[]>(props.rows.map(() => ''))
    const photoUploadProgress = ref<number[]>(props.rows.map(() => 0))

    // Per-row thumbnails for already-uploaded broker photos
    const photoThumbs = ref<OutputPhotoItem[][]>(props.rows.map(() => []))

    // Debounce timers per row index
    const timers: Record<number, any> = {}

    // Number formatter
    const nf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

    // WHAT: Normalize incoming rows for template
    // WHY: Create reactive copy of props.rows
    const normalizedRows = ref<BrokerFormEntry[]>(props.rows)
    
    // WHAT: Pagination and filter state (matching OverviewTab.vue)
    // WHY: Support filtering and pagination for large datasets
    const currentPage = ref(1)
    const pageSize = ref(20)  // Show 20 properties per page
    const filters = ref({
      search: '',  // Search by address or loan number
      state: '',   // Filter by state
      grade: '',   // Filter by broker grade
      valueSource: 'asis' as 'asis' | 'arv',  // Which value to filter on
      valueOperator: '>' as '>' | '<' | '=' | '>=' | '<=',  // Comparison operator
      valueAmount: null as number | null,  // Value threshold
    })
    
    // WHAT: Per-row grade state for broker-assigned grades
    // WHY: Track broker's quality assessment of each property
    const grades = ref<string[]>(props.rows.map(() => ''))
    
    // WHAT: Extract unique states from rows for filter dropdown
    // WHY: Populate state filter options dynamically
    const availableStates = computed(() => {
      const states = new Set<string>()
      if (normalizedRows.value) {
        normalizedRows.value.forEach((row: BrokerFormEntry) => {
          const state = extractState(row)
          if (state) states.add(state)
        })
      }
      return Array.from(states).sort()
    })
    
    // WHAT: Filtered rows based on all filter criteria
    // WHY: Allow brokers to quickly find specific properties
    const filteredRows = computed(() => {
      if (!normalizedRows.value) return []
      
      let filtered = normalizedRows.value
      
      // WHAT: Apply search filter (address or loan number)
      // WHY: Allow brokers to search their assignments
      if (filters.value.search) {
        const searchTerm = filters.value.search.toLowerCase()
        filtered = filtered.filter((row: BrokerFormEntry) => 
          (row.address || '').toLowerCase().includes(searchTerm) ||
          (getLoanNumber(row) || '').toLowerCase().includes(searchTerm)
        )
      }
      
      // WHAT: Apply state filter
      // WHY: Filter by specific state
      if (filters.value.state) {
        filtered = filtered.filter((row: BrokerFormEntry) => 
          extractState(row) === filters.value.state
        )
      }
      
      // WHAT: Apply grade filter
      // WHY: Filter by broker-assigned grade
      if (filters.value.grade) {
        if (filters.value.grade === 'none') {
          filtered = filtered.filter((row: BrokerFormEntry) => {
            const idx = normalizedRows.value.findIndex(r => r.key === row.key)
            return !grades.value[idx]
          })
        } else {
          filtered = filtered.filter((row: BrokerFormEntry) => {
            const idx = normalizedRows.value.findIndex(r => r.key === row.key)
            return grades.value[idx] === filters.value.grade
          })
        }
      }
      
      // WHAT: Apply value filter with operator
      // WHY: Allow flexible value filtering
      if (filters.value.valueAmount != null && filters.value.valueAmount > 0) {
        filtered = filtered.filter((row: BrokerFormEntry) => {
          const idx = normalizedRows.value.findIndex(r => r.key === row.key)
          // WHAT: Get the value based on selected source
          let value: number | null = null
          if (filters.value.valueSource === 'asis') {
            value = rowsState.value[idx]?.asIs ?? null
          } else {
            value = rowsState.value[idx]?.arv ?? null
          }
          
          if (value == null) return false
          
          // WHAT: Apply operator comparison
          const filterAmount = filters.value.valueAmount!
          switch (filters.value.valueOperator) {
            case '>': return value > filterAmount
            case '<': return value < filterAmount
            case '=': return value === filterAmount
            case '>=': return value >= filterAmount
            case '<=': return value <= filterAmount
            default: return true
          }
        })
      }
      
      return filtered
    })
    
    // WHAT: Total number of pages based on filtered results
    // WHY: Calculate pagination controls
    const totalPages = computed(() => Math.ceil(filteredRows.value.length / pageSize.value) || 1)
    
    // WHAT: Visible page numbers for pagination (show 5 pages max)
    // WHY: Match OverviewTab.vue pagination style
    const visiblePages = computed(() => {
      const pages: number[] = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })
    
    // WHAT: Paginated rows for current page
    // WHY: Show only rows for current page
    const paginatedRows = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredRows.value.slice(start, end)
    })

    // WHAT: Helper functions for table display and formatting
    // WHY: Extract address parts and format values consistently
    
    // WHAT: Get actual index in full normalizedRows array
    // WHY: paginatedRows shows subset, need to map back to full array index
    // HOW: Find entry in normalizedRows by key
    const getActualIndex = (entry: BrokerFormEntry): number => {
      return normalizedRows.value.findIndex(r => r.key === entry.key)
    }
    
    // WHAT: Extract loan number from entry
    // WHY: Display the actual loan number (sellertape_id) from backend
    // HOW: Use loan_number field from backend (added in hub-first refactor)
    const getLoanNumber = (entry: any): string => {
      // WHAT: Use loan_number from backend response (sellertape_id)
      // WHY: This is the actual loan identifier from seller's tape
      if (entry.loan_number) return String(entry.loan_number)
      // Fallback to asset_hub_id if loan_number not available
      return entry.srdId ? String(entry.srdId) : '-'
    }
    
    // WHAT: Extract street address from full address string
    // WHY: Show street separately from city/state
    // HOW: Take first part before comma
    const getStreetAddress = (entry: BrokerFormEntry): string => {
      const addr = entry.address || '-'
      const parts = addr.split(',')
      return parts[0]?.trim() || addr
    }
    
    // WHAT: Extract city and state from address string
    // WHY: Show on second line like OverviewTab.vue
    // HOW: Take parts after first comma
    const getCityState = (entry: BrokerFormEntry): string => {
      const addr = entry.address || ''
      const parts = addr.split(',').slice(1)
      return parts.join(',').trim() || '-'
    }
    
    // WHAT: Extract state from address string
    // WHY: Support state-based filtering
    // HOW: Look for 2-letter state code in address
    const extractState = (entry: BrokerFormEntry): string | null => {
      const addr = entry.address || ''
      // WHAT: Match 2-letter state codes (e.g., "CA", "NY", "TX")
      // WHY: Standard US state abbreviation format
      const match = addr.match(/\b([A-Z]{2})\b/)
      return match ? match[1] : null
    }
    
    // WHAT: Truncate text with ellipsis
    // WHY: Show preview of notes without taking too much space
    // HOW: Substring to maxLength and add ellipsis if truncated
    const truncateText = (text: string, maxLength: number): string => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }
    
    // WHAT: Get current grade for a row
    // WHY: Display in grade dropdown
    const getGrade = (idx: number): string => {
      return grades.value[idx] || ''
    }
    
    // WHAT: Handle save grade event
    // WHY: Store broker's quality assessment and trigger auto-save
    const handleSaveGrade = (idx: number, gradeCode: string) => {
      grades.value[idx] = gradeCode
      scheduleAutoSave(idx)
    }
    
    // WHAT: Format number with commas for display (no decimals)
    // WHY: Make large numbers more readable in filter input
    const formatNumberWithCommas = (val: number | null | undefined): string => {
      if (val == null) return ''
      return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(val)
    }
    
    // WHAT: Handle value filter input with comma formatting
    // WHY: Auto-format numbers as user types in filter input
    const handleValueFilterInput = (event: Event) => {
      const input = event.target as HTMLInputElement
      const rawValue = input.value.replace(/[^0-9]/g, '')
      
      if (rawValue === '') {
        filters.value.valueAmount = null
        input.value = ''
        return
      }
      
      const numericValue = parseInt(rawValue, 10)
      filters.value.valueAmount = numericValue
      input.value = formatNumberWithCommas(numericValue)
      
      applyFilters()
    }
    
    // WHAT: Apply filters and reset to page 1
    // WHY: User changed filter criteria, show first page of results
    const applyFilters = () => {
      currentPage.value = 1
    }
    
    // WHAT: Clear all filters and reset pagination
    // WHY: User wants to see all data again
    const clearFilters = () => {
      filters.value.search = ''
      filters.value.state = ''
      filters.value.grade = ''
      filters.value.valueSource = 'asis'
      filters.value.valueOperator = '>'
      filters.value.valueAmount = null
      currentPage.value = 1
    }
    
    // WHAT: Navigate to specific page
    // WHY: User clicks pagination controls
    const goToPage = (page: number) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }
    
    // WHAT: Open attachments modal for a row
    // WHY: Allow brokers to upload photos and documents in one place
    const openAttachmentsModal = (idx: number) => {
      // Load latest thumbnails before showing modal
      loadThumbnailsForRow(idx)
      attachmentsModalOpen.value[idx] = true
    }
    
    // WHAT: Open inspection report modal for a row
    // WHY: View/edit condition assessment and repair grades
    const openInspectionModal = (idx: number) => {
      inspectionModalOpen.value[idx] = true
    }
    
    // WHAT: Handle rehab breakdown updates
    // WHY: Save detailed repair grades and costs from broker
    // HOW: Auto-save to backend when broker edits any field
    const handleRehabUpdate = async (idx: number, data: Record<string, any>) => {
      console.log('[handleRehabUpdate] Called with idx:', idx, 'data:', data)
      
      const row = rowsState.value[idx]
      if (!row || !normalizedRows.value[idx]?.inviteToken) {
        console.warn('[handleRehabUpdate] No row or token at idx', idx)
        return
      }
      
      const token = normalizedRows.value[idx].inviteToken as string
      console.log('[handleRehabUpdate] Using token:', token)
      autoSaveStatus.value[idx] = 'saving'
      
      try {
        // WHAT: Prepare payload with rehab breakdown data
        const payload: Record<string, any> = {}
        
        // WHAT: Include all rehab fields from the breakdown
        const rehabFields = [
          'broker_roof_grade', 'broker_roof_est',
          'broker_kitchen_grade', 'broker_kitchen_est',
          'broker_bath_grade', 'broker_bath_est',
          'broker_flooring_grade', 'broker_flooring_est',
          'broker_windows_grade', 'broker_windows_est',
          'broker_appliances_grade', 'broker_appliances_est',
          'broker_plumbing_grade', 'broker_plumbing_est',
          'broker_electrical_grade', 'broker_electrical_est',
          'broker_landscaping_grade', 'broker_landscaping_est',
        ]
        
        rehabFields.forEach(field => {
          if (data[field] !== undefined) {
            // WHAT: Convert cost strings to numbers
            if (field.includes('_est')) {
              const val = String(data[field]).replace(/[^0-9]/g, '')
              payload[field] = val ? parseInt(val, 10) : null
            } else {
              payload[field] = data[field] || null
            }
          }
        })
        
        console.log('[handleRehabUpdate] Payload to send:', payload)
        
        // WHAT: Submit to broker values endpoint
        const response = await axios.post(`/api/acq/broker-invites/${token}/submit/`, payload)
        console.log('[handleRehabUpdate] Save successful:', response.data)
        
        autoSaveStatus.value[idx] = 'saved'
        setTimeout(() => {
          if (autoSaveStatus.value[idx] === 'saved') {
            autoSaveStatus.value[idx] = 'idle'
          }
        }, 2000)
      } catch (err) {
        console.error('[handleRehabUpdate] Save failed:', err)
        autoSaveStatus.value[idx] = 'error'
        saveMessage.value[idx] = 'Failed to save rehab data'
      }
    }
    
    // WHAT: Get total count of attachments (photos + documents)
    // WHY: Display badge count on attachments button
    const getTotalAttachments = (idx: number): number => {
      const photoCount = photoThumbs.value[idx]?.length || 0
      const docCount = rowsState.value[idx]?.docFiles?.length || 0
      return photoCount + docCount
    }
    
    // WHAT: Get summary text for attachments tooltip
    // WHY: Show breakdown of attachment types on hover
    const getAttachmentsSummary = (idx: number): string => {
      const photoCount = photoThumbs.value[idx]?.length || 0
      const docCount = rowsState.value[idx]?.docFiles?.length || 0
      if (photoCount === 0 && docCount === 0) return 'Upload attachments'
      const parts = []
      if (photoCount > 0) parts.push(`${photoCount} photo(s)`)
      if (docCount > 0) parts.push(`${docCount} document(s)`)
      return parts.join(', ')
    }
    
    // Helper: sanitize a string to digits only
    const sanitizeDigits = (val: string): string => (val || '').replace(/[^0-9]/g, '')

    // Helper: format digits with commas
    const formatWithCommas = (digits: string): string => {
      if (!digits) return ''
      try { return nf.format(Number(digits)) } catch { return digits }
    }
    
    // WHAT: Handle currency input with $ and comma formatting
    // WHY: Match OverviewTab.vue editable input behavior
    // HOW: Format as user types, store raw numeric value
    const handleCurrencyInput = (idx: number, field: 'asIs' | 'arv' | 'rehab', event: Event) => {
      const input = event.target as HTMLInputElement
      const rawValue = input.value.replace(/[^0-9]/g, '')
      
      if (!rawValue) {
        if (field === 'asIs') asIsInput.value[idx] = ''
        if (field === 'arv') arvInput.value[idx] = ''
        if (field === 'rehab') rehabInput.value[idx] = ''
        setRowFromDigits(idx, field, '')
        return
      }
      
      const numValue = parseInt(rawValue, 10)
      const formatted = '$' + nf.format(numValue)
      
      if (field === 'asIs') asIsInput.value[idx] = formatted
      if (field === 'arv') arvInput.value[idx] = formatted
      if (field === 'rehab') rehabInput.value[idx] = formatted
      
      setRowFromDigits(idx, field, rawValue)
    }
    
    // WHAT: Show link input field for a row
    // WHY: Allow broker to add new link
    const showLinkInput = (idx: number) => {
      linkInputVisible.value[idx] = true
    }
    
    // WHAT: Hide link input field
    // WHY: Return to clean display after adding or canceling
    const hideLinkInput = (idx: number) => {
      linkInput.value[idx] = ''
      linkInputVisible.value[idx] = false
    }
    
    // WHAT: Add link when user leaves input field or presses Enter
    // WHY: Simple paste-and-go UX without modal clicks
    // HOW: Validate URL, add to links array, hide input
    const addLinkOnBlur = (idx: number) => {
      const val = (linkInput.value[idx] || '').trim()
      if (!val) {
        // WHAT: If empty, just hide input
        hideLinkInput(idx)
        return
      }
      
      // WHAT: Basic URL validation
      // WHY: Ensure it's a valid URL before saving
      try {
        const url = new URL(val)
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
          hideLinkInput(idx)
          return  // Only allow http/https
        }
      } catch {
        hideLinkInput(idx)
        return  // Invalid URL, don't add
      }
      
      // WHAT: Add link, clear input, hide input field
      // WHY: Show only blue hyperlinks after adding
      rowsState.value[idx].links.push(val)
      linkInput.value[idx] = ''
      linkInputVisible.value[idx] = false
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      scheduleAutoSave(idx)
    }
    
    // WHAT: Remove a link from a row
    // WHY: Allow brokers to delete incorrectly added links
    const removeLink = (idx: number, linkIdx: number) => {
      rowsState.value[idx].links.splice(linkIdx, 1)
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      scheduleAutoSave(idx)
    }

    // WHAT: Client-side URL validation for Links input (per-row)
    // WHY: Validate URLs before allowing them to be added
    // HOW: Uses built-in URL constructor and enforces http/https protocol
    const linkValidity = ref<Array<'empty' | 'valid' | 'invalid'>>(
      props.rows.map(() => 'empty')
    )
    const linkError = ref<string[]>(props.rows.map(() => ''))

    // Validate a URL string using native URL; only http/https allowed
    const validateUrl = (val: string): { ok: boolean; reason?: string } => {
      if (!val || !val.trim()) return { ok: false, reason: 'Empty' }
      try {
        const u = new URL(val.trim())
        if (u.protocol === 'http:' || u.protocol === 'https:') return { ok: true }
        return { ok: false, reason: 'Only http/https allowed' }
      } catch {
        return { ok: false, reason: 'Malformed URL' }
      }
    }

    // Handle input change to update validity state
    const onLinkInput = (idx: number, raw: string) => {
      const v = (raw || '').trim()
      if (!v) {
        linkValidity.value[idx] = 'empty'
        linkError.value[idx] = ''
        return
      }
      const { ok, reason } = validateUrl(v)
      linkValidity.value[idx] = ok ? 'valid' : 'invalid'
      linkError.value[idx] = ok ? '' : (reason || 'Invalid URL')
    }

    // Helper: normalize numeric-ish to whole-dollar number
    const toWhole = (val: string | number | null | undefined): number | null => {
      if (val === null || val === undefined) return null
      const raw = String(val).replace(/,/g, '')
      const num = Number(raw)
      if (!Number.isFinite(num)) return null
      return Math.round(num)
    }

    // Set numeric from digits for a row and emit model update
    const setRowFromDigits = (idx: number, field: 'asIs' | 'arv' | 'rehab', digits: string) => {
      const num = digits ? Number(digits) : undefined
      rowsState.value[idx][field] = Number.isFinite(num as number) ? (num as number) : undefined
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
    }

    // WHAT: Hydrate from prefill values for each row
    // WHY: Load previously submitted broker data when portal loads
    // HOW: Map prefillValues to component state
    const applyPrefillAll = () => {
      normalizedRows.value.forEach((entry, idx) => {
        const v = entry.prefillValues
        if (!v) return
        // As-Is
        if (v.broker_asis_value !== undefined && v.broker_asis_value !== null) {
          const whole = toWhole(v.broker_asis_value)
          const d = whole !== null ? String(whole) : ''
          asIsInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'asIs', d)
        }
        // ARV
        if (v.broker_arv_value !== undefined && v.broker_arv_value !== null) {
          const whole = toWhole(v.broker_arv_value)
          const d = whole !== null ? String(whole) : ''
          arvInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'arv', d)
        }
        // Rehab
        if (v.broker_rehab_est !== undefined && v.broker_rehab_est !== null) {
          const whole = toWhole(v.broker_rehab_est)
          const d = whole !== null ? String(whole) : ''
          rehabInput.value[idx] = formatWithCommas(d)
          setRowFromDigits(idx, 'rehab', d)
        }
        // Notes
        if (typeof v.broker_notes === 'string') {
          rowsState.value[idx].notes = v.broker_notes || ''
          emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
        }
        // Grade (new field)
        if (typeof v.broker_grade === 'string') {
          grades.value[idx] = v.broker_grade || ''
        }
        // Links (single URLField in backend, map to first item in our list)
        if (typeof v.broker_links === 'string' && v.broker_links) {
          rowsState.value[idx].links = [v.broker_links]
          emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
        }
      })
    }

    // Initialize prefill on mount
    applyPrefillAll()

    // WHAT: React to changes in `rows` length/contents
    // WHY: Resize all per-row arrays when props.rows changes
    // HOW: Watch props.rows and rebuild all reactive arrays
    watch(
      () => props.rows,
      (newRows) => {
        normalizedRows.value = newRows || []
        // Resize per-row arrays to match new rows
        const n = normalizedRows.value.length
        rowsState.value = Array.from({ length: n }, (_, i) => rowsState.value[i] || {
          asIs: undefined,
          arv: undefined,
          rehab: undefined,
          notes: '',
          photoFiles: [],
          docFiles: [],
          links: [],
        })
        notesOpen.value = Array.from({ length: n }, (_, i) => notesOpen.value[i] || false)
        attachmentsModalOpen.value = Array.from({ length: n }, (_, i) => attachmentsModalOpen.value[i] || false)
        inspectionModalOpen.value = Array.from({ length: n }, (_, i) => inspectionModalOpen.value[i] || false)
        linksModalOpen.value = Array.from({ length: n }, (_, i) => linksModalOpen.value[i] || false)
        linkInputVisible.value = Array.from({ length: n }, (_, i) => linkInputVisible.value[i] || false)
        linkInput.value = Array.from({ length: n }, (_, i) => linkInput.value[i] || '')
        asIsInput.value = Array.from({ length: n }, (_, i) => asIsInput.value[i] || '')
        arvInput.value = Array.from({ length: n }, (_, i) => arvInput.value[i] || '')
        rehabInput.value = Array.from({ length: n }, (_, i) => rehabInput.value[i] || '')
        isSaving.value = Array.from({ length: n }, (_, i) => isSaving.value[i] || false)
        saveMessage.value = Array.from({ length: n }, (_, i) => saveMessage.value[i] || '')
        autoSaveStatus.value = Array.from({ length: n }, (_, i) => autoSaveStatus.value[i] || 'idle')
        photoUploadStatus.value = Array.from({ length: n }, (_, i) => photoUploadStatus.value[i] || 'idle')
        photoUploadMessage.value = Array.from({ length: n }, (_, i) => photoUploadMessage.value[i] || '')
        photoUploadProgress.value = Array.from({ length: n }, (_, i) => photoUploadProgress.value[i] || 0)
        photoThumbs.value = Array.from({ length: n }, (_, i) => photoThumbs.value[i] || [])
        photoViewerOpen.value = Array.from({ length: n }, (_, i) => photoViewerOpen.value[i] || false)
        linkValidity.value = Array.from({ length: n }, (_, i) => linkValidity.value[i] || 'empty')
        linkError.value = Array.from({ length: n }, (_, i) => linkError.value[i] || '')
        grades.value = Array.from({ length: n }, (_, i) => grades.value[i] || '')
        // Re-apply prefill for any new rows
        applyPrefillAll()
      },
      { deep: true }
    )

    // Fetch broker photo thumbnails for a row from the public photos API
    const loadThumbnailsForRow = async (idx: number) => {
      const srdId = normalizedRows.value[idx]?.srdId
      if (!srdId) {
        photoThumbs.value[idx] = []
        return
      }
      try {
        const { data } = await axios.get<OutputPhotoItem[]>(
          `/api/acq/photos/${encodeURIComponent(String(srdId))}/`,
          { withCredentials: false }
        )
        const items: OutputPhotoItem[] = Array.isArray(data) ? data : []
        // Show only broker-sourced images in this table cell
        photoThumbs.value[idx] = items.filter((p) => p && p.src && (p.type === 'broker'))
      } catch (err) {
        // Non-fatal; leave thumbnails empty on error
        photoThumbs.value[idx] = []
      }
    }

    // Initial load of thumbnails when component mounts
    onMounted(() => {
      normalizedRows.value.forEach((_, i) => loadThumbnailsForRow(i))
    })

    // When rows change (e.g., after parent refresh), reload thumbnails for visible rows
    watch(
      () => normalizedRows.value.map(r => r.srdId),
      () => {
        normalizedRows.value.forEach((_, i) => loadThumbnailsForRow(i))
      }
    )

    // Input formatter handler
    const onCurrencyModel = (idx: number, field: 'asIs' | 'arv' | 'rehab', val: string) => {
      const digits = sanitizeDigits(val || '')
      const formatted = formatWithCommas(digits)
      if (field === 'asIs') asIsInput.value[idx] = formatted
      if (field === 'arv') arvInput.value[idx] = formatted
      if (field === 'rehab') rehabInput.value[idx] = formatted
      setRowFromDigits(idx, field, digits)
      scheduleAutoSave(idx)
    }

    // Notes modal open
    const openNotes = (idx: number) => { notesOpen.value[idx] = true }

    // Photo viewer modal open handler. Ensures latest thumbnails are loaded before showing.
    const openPhotoViewer = async (idx: number) => {
      await loadThumbnailsForRow(idx)
      photoViewerOpen.value[idx] = true
    }

    // Save notes on modal OK
    const onSaveNotes = (idx: number) => {
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      scheduleAutoSave(idx)
    }

    // File selection handlers
    const onPhotoSelected = (idx: number, evt: Event) => {
      const input = evt.target as HTMLInputElement
      const files = input?.files ? Array.from(input.files) : []
      rowsState.value[idx].photoFiles = files
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      // Immediately upload selected photos for this row using the invite token
      if (files && files.length) {
        uploadPhotosForRow(idx)
      }
    }

    const onDocsSelected = (idx: number, evt: Event) => {
      const input = evt.target as HTMLInputElement
      const files = input?.files ? Array.from(input.files) : []
      rowsState.value[idx].docFiles = files
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
    }

    // Upload selected photos for a row to the backend token-based endpoint
    // Uses axios with onUploadProgress to report progress. Backend expects multipart
    // form field name 'files' (alias 'photos' or 'image' also accepted per backend docs).
    const uploadPhotosForRow = async (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      const files = rowsState.value[idx].photoFiles || []
      if (!token || !files.length) return

      // Initialize UI state for upload
      photoUploadStatus.value[idx] = 'uploading'
      photoUploadMessage.value[idx] = ''
      photoUploadProgress.value[idx] = 0

      try {
        const form = new FormData()
        for (const f of files) {
          // Append under canonical key 'files' (backend also supports 'photos'/'image')
          form.append('files', f)
        }

        const res = await axios.post(
          `/api/acq/broker-invites/${encodeURIComponent(token)}/photos/`,
          form,
          {
            headers: {
              // Let the browser set Content-Type with boundary; only declare Accept
              'Accept': 'application/json',
            },
            // Report upload progress for user feedback
            onUploadProgress: (evt: AxiosProgressEvent) => {
              if (typeof evt.total === 'number' && typeof evt.loaded === 'number' && evt.total > 0) {
                photoUploadProgress.value[idx] = Math.round((evt.loaded / evt.total) * 100)
              }
            },
            withCredentials: false,
          }
        )

        // Success: clear selected files, show message, and notify parent to refresh data
        const uploaded = Number((res?.data && (res.data.uploaded as any)) || files.length)
        rowsState.value[idx].photoFiles = []
        photoUploadStatus.value[idx] = 'uploaded'
        photoUploadMessage.value[idx] = `${uploaded} photo(s) uploaded`
        photoUploadProgress.value[idx] = 100
        // Refresh thumbnails for this row now that new photos exist
        await loadThumbnailsForRow(idx)
        emit('saved')
      } catch (e: any) {
        // Error: capture message and allow retry by re-selecting files
        photoUploadStatus.value[idx] = 'error'
        photoUploadMessage.value[idx] = e?.message || 'Upload failed'
      } finally {
        // No additional cleanup; keep progress bar at 100 on success briefly
        // Caller may trigger another selection to re-upload
      }
    }

    // Add link
    const addLink = (idx: number) => {
      const val = (linkInput.value[idx] || '').trim()
      // Guard: require a valid URL before adding
      if (!val) return
      if (linkValidity.value[idx] !== 'valid') return
      rowsState.value[idx].links.push(val)
      linkInput.value[idx] = ''
      // Reset validity state after adding
      linkValidity.value[idx] = 'empty'
      linkError.value[idx] = ''
      emit('update:modelValue', { ...props.modelValue, valuationRows: [...rowsState.value] })
      // Persist the new link automatically (backend expects a single URL string)
      scheduleAutoSave(idx)
    }

    // Debounced auto-save per row
    const scheduleAutoSave = (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      if (!token) return
      autoSaveStatus.value[idx] = 'saving'
      if (timers[idx]) clearTimeout(timers[idx])
      timers[idx] = setTimeout(() => submitNow(idx), 600)
    }

    // Immediate submit for a single row
    const submitNow = async (idx: number) => {
      const token = normalizedRows.value[idx]?.inviteToken
      if (!token) { autoSaveStatus.value[idx] = 'idle'; return }
      saveMessage.value[idx] = ''
      isSaving.value[idx] = true
      autoSaveStatus.value[idx] = 'saving'
      try {
        const payload: Record<string, any> = {
          broker_asis_value: rowsState.value[idx].asIs ?? null,
          broker_arv_value: rowsState.value[idx].arv ?? null,
          broker_rehab_est: rowsState.value[idx].rehab ?? null,
          broker_notes: rowsState.value[idx].notes || null,
          broker_grade: grades.value[idx] || null,  // WHAT: Include broker grade in payload
          broker_links: (rowsState.value[idx].links && rowsState.value[idx].links.length > 0)
            ? rowsState.value[idx].links[0]
            : null,
        }
        const res = await fetch(`/api/acq/broker-invites/${encodeURIComponent(token)}/submit/`, {
          method: 'POST',
          headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
          credentials: 'same-origin',
          body: JSON.stringify(payload),
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err?.detail || 'Failed to save')
        }
        autoSaveStatus.value[idx] = 'saved'
        saveMessage.value[idx] = ''
        // Notify parent so it can refresh portal payload if needed
        emit('saved')
      } catch (e: any) {
        autoSaveStatus.value[idx] = 'error'
        saveMessage.value[idx] = e?.message || 'Save failed'
      } finally {
        isSaving.value[idx] = false
      }
    }

    return {
      // WHAT: Data and state
      normalizedRows,
      rowsState,
      grades,
      notesOpen,
      attachmentsModalOpen,
      inspectionModalOpen,
      linksModalOpen,
      linkInputVisible,
      linkInput,
      linkValidity,
      linkError,
      asIsInput,
      arvInput,
      rehabInput,
      isSaving,
      saveMessage,
      autoSaveStatus,
      photoUploadStatus,
      photoUploadMessage,
      photoUploadProgress,
      photoThumbs,
      photoViewerOpen,
      // WHAT: Pagination and filtering
      filters,
      availableStates,
      filteredRows,
      paginatedRows,
      currentPage,
      totalPages,
      visiblePages,
      // WHAT: Helper functions
      getActualIndex,
      getLoanNumber,
      getStreetAddress,
      getCityState,
      extractState,
      truncateText,
      getGrade,
      handleSaveGrade,
      formatNumberWithCommas,
      handleValueFilterInput,
      applyFilters,
      clearFilters,
      goToPage,
      handleCurrencyInput,
      openAttachmentsModal,
      getTotalAttachments,
      getAttachmentsSummary,
      openInspectionModal,
      handleRehabUpdate,
      showLinkInput,
      hideLinkInput,
      addLinkOnBlur,
      removeLink,
      // WHAT: Original functions
      onCurrencyModel,
      openNotes,
      openPhotoViewer,
      onSaveNotes,
      onPhotoSelected,
      onDocsSelected,
      uploadPhotosForRow,
      loadThumbnailsForRow,
      addLink,
      onLinkInput,
      scheduleAutoSave,
      submitNow,
    }
  },
})
</script>

<style scoped>
/* WHAT: Editable inline input fields styled in blue (matching OverviewTab.vue) */
/* WHY: Visual indicator that these values are editable by the broker */
.editable-value-inline {
  border: none;
  background: transparent;
  text-align: center;
  width: 120px;
  padding: 4px 8px;
  font-size: inherit;
  color: #3577f1;
  font-weight: 500;
  cursor: pointer;
}

/* WHAT: Blue italicized placeholder text for editable inputs */
/* WHY: Consistent blue styling to indicate this field is user-editable */
.editable-value-inline::placeholder {
  color: #3577f1;
  opacity: 0.7;
  font-style: italic;
}

.editable-value-inline:hover {
  background-color: #e7f1ff;
  border: 1px solid #3577f1;
  border-radius: 3px;
}

.editable-value-inline:focus {
  outline: none;
  background-color: #fff;
  border: 1px solid #3577f1;
  border-radius: 3px;
  color: #3577f1;
}

/* WHAT: Grade select dropdown styling */
/* WHY: Compact inline display in table cell */
.grade-select {
  width: auto;
  min-width: 70px;
  display: inline-block;
}

/* WHAT: Notes preview container - clickable cell */
/* WHY: Make entire cell clickable to edit notes */
.notes-preview-container {
  cursor: pointer;
  padding: 6px 8px;
  min-height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notes-preview-container:hover {
  background-color: #f8f9fa;
}

/* WHAT: Container for notes text + icon */
/* WHY: Align text and icon together */
.notes-with-icon {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  max-width: 200px;
}

/* WHAT: Multi-line notes text (wraps to 2 lines max) */
/* WHY: Show more context than single line */
.notes-text-multiline {
  font-size: 0.875rem;
  color: #495057;
  line-height: 1.3;
  text-align: left;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
}

/* WHAT: Small edit icon at end of text */
/* WHY: Visual indicator that note is editable */
.notes-edit-icon {
  font-size: 0.875rem;
  color: #6c757d;
  opacity: 0.7;
  flex-shrink: 0;
  margin-top: 2px;
}

.notes-preview-container:hover .notes-text-multiline {
  color: #3577f1;
}

.notes-preview-container:hover .notes-edit-icon {
  color: #3577f1;
  opacity: 1;
}

/* WHAT: Placeholder for empty notes */
/* WHY: Clear call-to-action when no note exists */
.notes-placeholder {
  font-size: 0.875rem;
  color: #6c757d;
  font-style: italic;
}

.notes-placeholder:hover {
  color: #3577f1;
}

/* WHAT: Links cell container */
/* WHY: Clean vertical layout for input and saved links */
.links-cell {
  padding: 4px;
  min-width: 200px;
  text-align: center;
}

/* WHAT: Add Link text (clickable) */
/* WHY: Center, italicize, no icon - matches value input blue */
.add-link-text {
  font-size: 0.875rem;
  color: #3577f1;
  font-style: italic;
  cursor: pointer;
  opacity: 0.7;
}

.add-link-text:hover {
  opacity: 1;
}

/* WHAT: Saved links list */
/* WHY: Display multiple links vertically */
.saved-links-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

/* WHAT: Individual saved link item */
/* WHY: Show link with delete button inline */
.saved-link-item {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  padding: 2px 0;
}

/* WHAT: Truncated link text */
/* WHY: Prevent long URLs from breaking layout */
.link-truncated {
  color: #3577f1;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.link-truncated:hover {
  text-decoration: underline;
}

/* WHAT: Link remove button */
/* WHY: Inline X button to delete link */
.btn-link-remove {
  background: none;
  border: none;
  color: #dc3545;
  padding: 0;
  margin-left: 6px;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  opacity: 0.6;
}

.btn-link-remove:hover {
  opacity: 1;
}

/* Hide spinner arrows in number inputs within this component */
/* Chrome, Safari, Edge, Opera */
.table input[type='number']::-webkit-outer-spin-button,
.table input[type='number']::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
.table input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield; /* modern standardized property */
}
</style>
