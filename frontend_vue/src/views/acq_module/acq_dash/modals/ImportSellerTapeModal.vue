<template>
  <!--
    ImportSellerTapeModal - Upload and process seller data tapes
    WHAT: Drag-and-drop file upload with ETL processing
    WHY: Allow users to import Excel/CSV files directly from the UI
    HOW: Upload file to backend, trigger Django management command, show progress
  -->
  <div class="import-seller-tape-modal">
    <!-- Step 1: File Upload -->
    <div v-if="step === 'upload'" class="upload-section">
      <div
        class="drop-zone"
        :class="{ 'drag-over': isDragging, 'has-file': selectedFile }"
        @drop.prevent="handleDrop"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
      >
        <div v-if="!selectedFile" class="drop-zone-content">
          <i class="mdi mdi-cloud-upload display-4 text-muted mb-3"></i>
          <h5>Drag & Drop File Here</h5>
          <p class="text-muted">or</p>
          <label class="btn btn-primary">
            <i class="mdi mdi-folder-open me-2"></i>Browse Computer
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              accept=".xlsx,.xls,.csv"
              style="display: none"
            />
          </label>
          <p class="text-muted mt-3 mb-0">
            <small>Supported formats: Excel (.xlsx, .xls) or CSV (.csv)</small>
          </p>
        </div>

        <div v-else class="selected-file-info">
          <i class="mdi mdi-file-excel display-4 text-success mb-3"></i>
          <h5>{{ selectedFile.name }}</h5>
          <p class="text-muted">{{ formatFileSize(selectedFile.size) }}</p>
          <button class="btn btn-sm btn-outline-danger" @click="clearFile">
            <i class="mdi mdi-close me-1"></i>Remove File
          </button>
        </div>
      </div>

      <!-- Import Options -->
      <div v-if="selectedFile" class="mt-4">
        <h6>Import Options</h6>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Seller <span class="text-danger">*</span></label>
            <select
              v-model="selectedSellerId"
              class="form-select"
              :disabled="sellersLoading"
              required
            >
              <option value="manual">+ Manually add new seller</option>
              <option
                v-for="option in sellerOptions"
                :key="option.id"
                :value="option.id"
              >
                {{ option.name }}
              </option>
            </select>
            <small v-if="sellersError" class="text-danger d-block mt-1">{{ sellersError }}</small>
            <small v-else class="form-text text-muted">Choose an existing seller or add a new one.</small>
            <input
              v-if="selectedSellerId === 'manual'"
              v-model="sellerName"
              type="text"
              class="form-control mt-2"
              placeholder="Enter seller name"
              required
            />
            <div v-else class="form-control mt-2 bg-light" readonly>
              {{ sellerName || 'Select a seller' }}
            </div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Trade Name <span class="text-muted">(Optional)</span></label>
            <input
              v-model="tradeName"
              type="text"
              class="form-control"
              placeholder="Leave blank to auto-generate"
            />
            <small class="form-text text-muted">Auto-generated as "SellerName - MM.DD.YY" if blank</small>
          </div>
          <div class="col-12">
            <div class="form-check mb-2">
              <input
                v-model="dryRun"
                class="form-check-input"
                type="checkbox"
                id="dryRunCheck"
              />
              <label class="form-check-label" for="dryRunCheck">
                Dry run (preview only, don't save to database)
              </label>
            </div>
            <div class="form-check">
              <input
                v-model="noAi"
                class="form-check-input"
                type="checkbox"
                id="noAiCheck"
                :disabled="useManualMapping"
              />
              <label class="form-check-label" for="noAiCheck">
                Disable AI column mapping (faster for large files, uses default mapping)
              </label>
            </div>
            <div class="form-check">
              <input
                v-model="useManualMapping"
                class="form-check-input"
                type="checkbox"
                id="manualMappingCheck"
              />
              <label class="form-check-label" for="manualMappingCheck">
                <strong>Manual column mapping</strong> (review and map columns before import)
              </label>
            </div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Test Mode <span class="text-muted">(Limit Rows)</span></label>
            <input
              v-model="limitRows"
              type="number"
              class="form-control"
              placeholder="e.g., 1 for testing"
              min="1"
            />
            <small class="form-text text-muted">Process only first N rows (useful for testing without API costs)</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Manual Column Mapping -->
    <div v-if="step === 'mapping'" class="mapping-section">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h6 class="mb-0">
          <i class="mdi mdi-table-column me-2"></i>Map Columns
        </h6>
        <span class="badge bg-info">{{ previewData?.row_count || 0 }} rows detected</span>
      </div>
      <p class="text-muted small mb-3">
        Map source columns from your file to our database fields. AI detected the header row automatically.
      </p>
      
      <div class="mapping-table-container" style="max-height: 400px; overflow-y: auto;">
        <table class="table table-sm table-hover">
          <thead class="sticky-top bg-white">
            <tr>
              <th style="width: 40%">Source Column</th>
              <th style="width: 30%">Sample Data</th>
              <th style="width: 30%">Map To Field</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="col in previewData?.source_columns || []" :key="col">
              <td>
                <code class="text-primary">{{ col }}</code>
              </td>
              <td class="small text-muted">
                <span v-for="(sample, idx) in (previewData?.sample_data?.[col] || [])" :key="idx">
                  {{ sample }}<span v-if="idx < (previewData?.sample_data?.[col]?.length || 0) - 1">, </span>
                </span>
              </td>
              <td>
                <div class="field-autocomplete position-relative">
                  <input
                    type="text"
                    class="form-control form-control-sm"
                    :placeholder="columnMapping[col] || '-- Skip --'"
                    v-model="searchTerms[col]"
                    @focus="activeDropdown = col"
                    @blur="handleBlur(col)"
                    @keydown.down.prevent="navigateDown(col)"
                    @keydown.up.prevent="navigateUp(col)"
                    @keydown.enter.prevent="selectHighlighted(col)"
                    @keydown.escape="activeDropdown = ''"
                  />
                  <div
                    v-if="activeDropdown === col && filteredFields(col).length > 0"
                    class="autocomplete-dropdown"
                  >
                    <div
                      class="autocomplete-item"
                      :class="{ active: highlightedIndex[col] === -1 }"
                      @mousedown.prevent="selectField(col, '')"
                    >
                      <span class="text-muted">-- Skip --</span>
                    </div>
                    <div
                      v-for="(field, idx) in filteredFields(col)"
                      :key="field.name"
                      class="autocomplete-item"
                      :class="{ active: highlightedIndex[col] === idx }"
                      @mousedown.prevent="selectField(col, field.name)"
                    >
                      <span class="field-name">{{ field.name }}</span>
                      <span v-if="field.matchedAlias" class="field-alias text-muted ms-2">
                        ({{ field.matchedAlias }})
                      </span>
                    </div>
                  </div>
                  <span v-if="columnMapping[col]" class="selected-badge">
                    {{ columnMapping[col] }}
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="mt-3 p-2 bg-light rounded">
        <small class="text-muted">
          <i class="mdi mdi-information-outline me-1"></i>
          <strong>Required:</strong> Map at least <code>sellertape_id</code> (unique loan identifier).
          Unmapped columns will be skipped.
        </small>
      </div>
    </div>

    <!-- Step 3: Processing -->
    <div v-if="step === 'processing'" class="processing-section text-center py-5">
      <div class="spinner-border text-primary mb-3" role="status">
        <span class="visually-hidden">Processing...</span>
      </div>
      <h5>Processing Import...</h5>
      <p class="text-muted">{{ processingMessage }}</p>
    </div>

    <!-- Step 3: Results -->
    <div v-if="step === 'results'" class="results-section">
      <div v-if="importSuccess" class="alert alert-success">
        <i class="mdi mdi-check-circle me-2"></i>
        <strong>Import Successful!</strong>
        <p class="mb-0 mt-2">{{ importResults }}</p>
      </div>
      <div v-else class="alert alert-danger">
        <i class="mdi mdi-alert-circle me-2"></i>
        <strong>Import Failed</strong>
        <pre class="mb-0 mt-2" style="white-space: pre-wrap; font-family: inherit;">{{ importError }}</pre>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="d-flex justify-content-end gap-2 mt-4 pt-3 border-top">
      <button
        v-if="step === 'upload'"
        class="btn btn-secondary"
        @click="$emit('close')"
      >
        Cancel
      </button>
      <button
        v-if="step === 'upload'"
        class="btn btn-primary"
        @click="startImport"
        :disabled="!selectedFile || !sellerName"
      >
        <i class="mdi mdi-upload me-1"></i>{{ useManualMapping ? 'Next: Map Columns' : 'Start Import' }}
      </button>
      <!-- Mapping step buttons -->
      <button
        v-if="step === 'mapping'"
        class="btn btn-secondary"
        @click="step = 'upload'"
      >
        <i class="mdi mdi-arrow-left me-1"></i>Back
      </button>
      <button
        v-if="step === 'mapping'"
        class="btn btn-primary"
        @click="proceedWithImport"
        :disabled="!hasSellertapeIdMapping"
      >
        <i class="mdi mdi-upload me-1"></i>Import with Mapping
      </button>
      <button
        v-if="step === 'results'"
        class="btn btn-primary"
        @click="resetModal"
      >
        Import Another File
      </button>
      <button
        v-if="step === 'results'"
        class="btn btn-success"
        @click="handleDone"
      >
        Done
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, reactive } from 'vue'
import axios from '@/lib/http'

/**
 * WHAT: Type definition describing each seller option returned by the API.
 * WHY: Keeps the dropdown strongly typed for TypeScript correctness.
 */
interface SellerOption {
  id: number // WHAT: Database identifier for the seller option
  name: string // WHAT: Human-friendly seller display name
}

/**
 * WHAT: Type definition for preview data returned by backend
 * WHY: Provides structure for manual column mapping
 */
interface PreviewData {
  source_columns: string[]
  target_fields: Array<{ name: string; type: string; description: string }>
  sample_data: Record<string, string[]>
  row_count: number
  file_name: string
}

// Emits
const emit = defineEmits<{
  close: []
  success: [payload?: { sellerId: number; tradeId: number }]
  refresh: []
}>()

// State
const step = ref<'upload' | 'mapping' | 'processing' | 'results'>('upload') // WHAT: Current wizard stage
const isDragging = ref(false) // WHAT: Tracks drag-over styling state for drop zone
const selectedFile = ref<File | null>(null) // WHAT: User-selected file reference
const fileInput = ref<HTMLInputElement | null>(null) // WHAT: Hidden input reference for programmatic reset

// Import options
const sellerName = ref('') // WHAT: Seller name used for backend processing
const tradeName = ref('') // WHAT: Optional trade label override supplied by user
const dryRun = ref(false) // WHAT: Checkbox state toggling preview-only mode
const noAi = ref(false) // WHAT: Checkbox state to disable AI column mapping for faster imports
const limitRows = ref<number | ''>('') // WHAT: Limit to first N rows for testing
const sellerOptions = ref<SellerOption[]>([]) // WHAT: Cached list of seller dropdown options
const selectedSellerId = ref<number | 'manual'>('manual') // WHAT: Currently chosen seller id or manual flag
const sellersLoading = ref(false) // WHAT: Loading indicator while fetching seller options
const sellersError = ref('') // WHAT: Error message to surface when seller fetch fails

// Manual mapping state
const useManualMapping = ref(false) // WHAT: Toggle for manual column mapping mode
const previewData = ref<PreviewData | null>(null) // WHAT: File preview data from backend
const columnMapping = reactive<Record<string, string>>({}) // WHAT: User-defined column mappings

// Autocomplete state
const searchTerms = reactive<Record<string, string>>({}) // WHAT: Search input per column
const activeDropdown = ref('') // WHAT: Which column's dropdown is open
const highlightedIndex = reactive<Record<string, number>>({}) // WHAT: Keyboard nav index per column

/**
 * WHAT: Natural language aliases for target fields
 * WHY: Allow users to type common terms like "loan id" to find "sellertape_id"
 */
const fieldAliases: Record<string, string[]> = {
  sellertape_id: ['loan id', 'loan number', 'id', 'number', 'loan #', 'loan_id', 'loan_number', 'identifier', 'acct', 'account'],
  sellertape_altid: ['alt id', 'alternative id', 'secondary id', 'other id', 'alt_id', 'alt number'],
  street_address: ['address', 'street', 'property address', 'addr', 'location'],
  city: ['city', 'town', 'municipality'],
  state: ['state', 'st', 'province'],
  zip: ['zip', 'zipcode', 'zip code', 'postal', 'postal code'],
  property_type: ['property type', 'prop type', 'type', 'dwelling'],
  product_type: ['product', 'loan type', 'product type'],
  current_balance: ['balance', 'upb', 'current balance', 'principal balance', 'loan balance', 'unpaid balance'],
  total_debt: ['debt', 'total debt', 'total owed', 'amount owed'],
  interest_rate: ['rate', 'interest', 'interest rate', 'note rate', 'coupon'],
  original_balance: ['original', 'original balance', 'orig balance', 'orig upb'],
  as_of_date: ['as of', 'date', 'as of date', 'tape date', 'data date'],
  occupancy: ['occupancy', 'occupied', 'vacant', 'occupancy status'],
  asset_status: ['status', 'asset status', 'loan status', 'npl', 'reo'],
  seller_asis_value: ['value', 'bpo', 'as is', 'as-is', 'asis value', 'property value'],
  seller_repaired_value: ['arv', 'repaired', 'after repair', 'repaired value'],
  borrower_name: ['borrower', 'name', 'borrower name', 'customer'],
  origination_date: ['orig date', 'origination', 'origination date', 'originated'],
  maturity_date: ['maturity', 'maturity date', 'mat date'],
  last_paid_date: ['last paid', 'lpd', 'last payment', 'last pay date'],
  next_due_date: ['next due', 'due date', 'payment due'],
  delinquency_days: ['days', 'delinquent', 'delinquency', 'days delinquent', 'dpd'],
  monthly_payment: ['payment', 'piti', 'monthly', 'p&i', 'pi'],
  escrow_balance: ['escrow', 'escrow balance', 'impound'],
  taxes: ['taxes', 'tax', 'property tax'],
  insurance: ['insurance', 'ins', 'hazard'],
  hoa: ['hoa', 'association', 'hoa dues'],
  legal_fees: ['legal', 'legal fees', 'attorney fees'],
  lien_position: ['lien', 'position', 'lien position', '1st', '2nd'],
  county: ['county'],
  beds: ['beds', 'bedrooms', 'br'],
  baths: ['baths', 'bathrooms', 'ba'],
  sqft: ['sqft', 'square feet', 'sq ft', 'size', 'square footage'],
  lot_size: ['lot', 'lot size', 'acreage', 'acres'],
  year_built: ['year', 'year built', 'built', 'age'],
}

/**
 * WHAT: Check if sellertape_id is mapped (required for import)
 * WHY: sellertape_id is the unique identifier required for each loan
 */
const hasSellertapeIdMapping = computed(() => {
  return Object.values(columnMapping).includes('sellertape_id')
})

/**
 * WHAT: Filter target fields based on search term with natural language matching
 * WHY: Enable typing "loan id" to find "sellertape_id"
 */
function filteredFields(col: string) {
  const search = (searchTerms[col] || '').toLowerCase().trim()
  const fields = previewData.value?.target_fields || []
  
  if (!search) {
    // Return all fields when no search term, sorted alphabetically
    return fields.map(f => ({ ...f, matchedAlias: '' }))
  }
  
  // Score and filter fields
  const scored = fields.map(field => {
    const fieldName = field.name.toLowerCase()
    const aliases = fieldAliases[field.name] || []
    
    // Check direct field name match
    if (fieldName.includes(search)) {
      return { ...field, matchedAlias: '', score: fieldName === search ? 100 : 50 }
    }
    
    // Check alias matches
    for (const alias of aliases) {
      if (alias.includes(search) || search.includes(alias)) {
        return { ...field, matchedAlias: alias, score: alias === search ? 90 : 40 }
      }
    }
    
    // Fuzzy: check if search words appear in field name
    const searchWords = search.split(/[\s_]+/)
    const fieldWords = fieldName.split('_')
    const matchedWords = searchWords.filter(sw => 
      fieldWords.some(fw => fw.includes(sw) || sw.includes(fw))
    )
    if (matchedWords.length > 0) {
      return { ...field, matchedAlias: '', score: matchedWords.length * 10 }
    }
    
    return null
  }).filter(f => f !== null) as Array<{ name: string; type: string; description: string; matchedAlias: string; score: number }>
  
  // Sort by score descending
  return scored.sort((a, b) => b.score - a.score)
}

/**
 * WHAT: Select a field for a column mapping
 */
function selectField(col: string, fieldName: string) {
  columnMapping[col] = fieldName
  searchTerms[col] = ''
  activeDropdown.value = ''
  highlightedIndex[col] = 0
}

/**
 * WHAT: Handle blur with delay to allow click on dropdown items
 */
function handleBlur(col: string) {
  setTimeout(() => {
    if (activeDropdown.value === col) {
      activeDropdown.value = ''
    }
  }, 150)
}

/**
 * WHAT: Keyboard navigation - move down in dropdown
 */
function navigateDown(col: string) {
  const filtered = filteredFields(col)
  const current = highlightedIndex[col] ?? -1
  highlightedIndex[col] = Math.min(current + 1, filtered.length - 1)
}

/**
 * WHAT: Keyboard navigation - move up in dropdown
 */
function navigateUp(col: string) {
  const current = highlightedIndex[col] ?? 0
  highlightedIndex[col] = Math.max(current - 1, -1)
}

/**
 * WHAT: Select the currently highlighted item
 */
function selectHighlighted(col: string) {
  const idx = highlightedIndex[col] ?? -1
  if (idx === -1) {
    selectField(col, '')
  } else {
    const filtered = filteredFields(col)
    if (filtered[idx]) {
      selectField(col, filtered[idx].name)
    }
  }
}

// Processing state
const processingMessage = ref('Uploading file and analyzing columns...') // WHAT: Status text displayed during import
const importSuccess = ref(false) // WHAT: Tracks whether backend reported success
const importResults = ref('') // WHAT: Success payload provided by backend
const importError = ref('') // WHAT: Error payload provided by backend
const importedData = ref<{ sellerId: number; tradeId: number } | null>(null) // WHAT: Store imported IDs for auto-selection

/**
 * WHAT: Apply dropdown selection to local state and auto-create toggle.
 * WHY: Ensures manual entry clears sellerName while existing selections populate it.
 */
const applySellerSelection = (nextValue: number | 'manual'): void => {
  if (nextValue === 'manual') {
    sellerName.value = ''
    return
  }
  const match = sellerOptions.value.find((option) => option.id === nextValue)
  sellerName.value = match?.name ?? ''
}

/**
 * WHAT: Retrieve seller dropdown options from acquisitions API endpoint.
 * WHY: Powers dropdown choices to encourage reuse over manual entry.
 * DOCS: https://axios-http.com/docs/api_intro for request patterns.
 */
const fetchSellerOptions = async (): Promise<void> => {
  sellersLoading.value = true
  sellersError.value = ''
  try {
    const response = await axios.get<SellerOption[]>('/acq/sellers/', {
      params: { view: 'all' },
    })
    const payload = Array.isArray(response.data) ? response.data : []
    sellerOptions.value = payload.map((option) => ({
      id: option.id,
      name: String(option.name ?? '').toUpperCase(),
    }))
  } catch (error: any) {
    sellersError.value = error?.message || 'Failed to load sellers'
  } finally {
    sellersLoading.value = false
    applySellerSelection(selectedSellerId.value)
  }
}

// WHAT: React to dropdown changes to keep sellerName synced.
watch(selectedSellerId, (nextValue) => applySellerSelection(nextValue))

// WHAT: Prime seller dropdown on mount so users see options immediately.
onMounted(() => {
  void fetchSellerOptions()
})

/**
 * Handle file drop
 */
function handleDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

/**
 * Handle file selection from browse
 */
function handleFileSelect(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]
  }
}

/**
 * Clear selected file
 */
function clearFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

/**
 * Start import process - either preview for mapping or direct import
 */
async function startImport() {
  if (!selectedFile.value || !sellerName.value) return

  // If manual mapping is enabled, first get preview data
  if (useManualMapping.value) {
    step.value = 'processing'
    processingMessage.value = 'Analyzing file headers...'
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      
      const response = await axios.post('/acq/preview-seller-tape/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000, // 1 minute for preview
      })
      
      // Store preview data and reset column mapping
      previewData.value = response.data
      Object.keys(columnMapping).forEach(key => delete columnMapping[key])
      
      // Initialize empty mappings for all source columns
      if (response.data.source_columns) {
        response.data.source_columns.forEach((col: string) => {
          columnMapping[col] = ''
        })
      }
      
      step.value = 'mapping'
    } catch (error: any) {
      step.value = 'results'
      importSuccess.value = false
      importError.value = error.response?.data?.error || error.message || 'Failed to preview file'
      console.error('Preview error:', error)
    }
    return
  }

  // Direct import (no manual mapping)
  await executeImport()
}

/**
 * Proceed with import after manual mapping
 */
async function proceedWithImport() {
  await executeImport()
}

/**
 * Execute the actual import with optional column mapping
 */
async function executeImport() {
  if (!selectedFile.value || !sellerName.value) return

  step.value = 'processing'
  processingMessage.value = 'Uploading file and importing data...'

  try {
    // Create form data
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('seller_name', sellerName.value)
    if (tradeName.value) formData.append('trade_name', tradeName.value)
    formData.append('dry_run', dryRun.value.toString())
    formData.append('no_ai', noAi.value.toString())
    if (limitRows.value) formData.append('limit_rows', limitRows.value.toString())
    
    // Add manual column mapping if we have one
    if (useManualMapping.value && Object.keys(columnMapping).length > 0) {
      // Filter out empty mappings (skipped columns)
      const filteredMapping: Record<string, string> = {}
      Object.entries(columnMapping).forEach(([source, target]) => {
        if (target) {
          filteredMapping[source] = target
        }
      })
      formData.append('column_mapping', JSON.stringify(filteredMapping))
    }

    // Call backend API endpoint
    const response = await axios.post('/acq/import-seller-tape/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      // Allow lengthy ETL processing for large files (20 minutes for 600+ records)
      timeout: 1200000,
    })

    // Success
    step.value = 'results'
    importSuccess.value = true
    
    // Build detailed success message
    const data = response.data
    let successMsg = data.message || 'Import completed successfully!'
    if (data.seller_name) {
      successMsg += `\n\nSeller: ${data.seller_name}`
    }
    if (data.records_imported) {
      successMsg += `\nRecords: ${data.records_imported}`
    }
    importResults.value = successMsg
    
    // Store imported IDs for auto-selection when user clicks Done
    if (data.seller_id && data.trade_id) {
      importedData.value = { sellerId: data.seller_id, tradeId: data.trade_id }
    }
    
    // Refresh data but don't auto-close
    emit('refresh')
  } catch (error: any) {
    // Error - show detailed error message
    step.value = 'results'
    importSuccess.value = false
    
    // Build detailed error message
    let errorMsg = 'Import failed'
    if (error.response?.data) {
      const data = error.response.data
      errorMsg = data.error || data.message || 'Import failed'
      if (data.details) {
        errorMsg += '\n\nDetails:\n' + data.details
      }
      if (data.output) {
        errorMsg += '\n\nOutput:\n' + data.output
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    importError.value = errorMsg
    console.error('Import error:', error)
  }
}

/**
 * Handle Done button - emit success with IDs and close
 */
function handleDone() {
  if (importedData.value) {
    emit('success', importedData.value)
  } else {
    emit('success')
  }
  emit('close')
}

/**
 * Reset modal to initial state
 */
function resetModal() {
  step.value = 'upload'
  selectedFile.value = null
  sellerName.value = ''
  tradeName.value = ''
  dryRun.value = false
  noAi.value = false
  limitRows.value = ''
  useManualMapping.value = false
  previewData.value = null
  Object.keys(columnMapping).forEach(key => delete columnMapping[key])
  Object.keys(searchTerms).forEach(key => delete searchTerms[key])
  Object.keys(highlightedIndex).forEach(key => delete highlightedIndex[key])
  activeDropdown.value = ''
  importSuccess.value = false
  importResults.value = ''
  importError.value = ''
  importedData.value = null
  selectedSellerId.value = 'manual'
  applySellerSelection('manual')
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed #dee2e6;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.drop-zone.drag-over {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

.drop-zone.has-file {
  border-color: #198754;
  background-color: #d1e7dd;
}

.drop-zone-content i {
  opacity: 0.5;
}

.selected-file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

/* Manual mapping table styles */
.mapping-section {
  min-height: 300px;
}

.mapping-table-container {
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

.mapping-table-container thead th {
  background-color: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 1;
}

.mapping-table-container tbody tr:hover {
  background-color: #f8f9fa;
}

.mapping-table-container code {
  font-size: 0.85em;
  padding: 0.1em 0.3em;
  background-color: #e9ecef;
  border-radius: 3px;
}

/* Autocomplete dropdown styles */
.field-autocomplete {
  position: relative;
}

.field-autocomplete input {
  padding-right: 80px;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: #FDFBF7;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.autocomplete-item {
  padding: 6px 10px;
  cursor: pointer;
  font-size: 0.85em;
  border-bottom: 1px solid #f0f0f0;
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.autocomplete-item:hover,
.autocomplete-item.active {
  background-color: #e7f1ff;
}

.autocomplete-item .field-name {
  font-weight: 500;
}

.autocomplete-item .field-alias {
  font-size: 0.8em;
  font-style: italic;
}

.selected-badge {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.7em;
  background-color: #198754;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  pointer-events: none;
}
</style>
