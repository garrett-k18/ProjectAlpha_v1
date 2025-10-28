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
            <div class="form-check">
              <input
                v-model="autoCreate"
                class="form-check-input"
                type="checkbox"
                id="autoCreateCheck"
              />
              <label class="form-check-label" for="autoCreateCheck">
                Auto-create seller and trade if they don't exist
              </label>
            </div>
          </div>
          <div class="col-12">
            <div class="form-check">
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
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Processing -->
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
        <i class="mdi mdi-upload me-1"></i>Start Import
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
        @click="$emit('close')"
      >
        Done
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'

/**
 * WHAT: Type definition describing each seller option returned by the API.
 * WHY: Keeps the dropdown strongly typed for TypeScript correctness.
 */
interface SellerOption {
  id: number // WHAT: Database identifier for the seller option
  name: string // WHAT: Human-friendly seller display name
}

// Emits
const emit = defineEmits<{
  close: []
  success: []
  refresh: []
}>()

// State
const step = ref<'upload' | 'processing' | 'results'>('upload') // WHAT: Current wizard stage
const isDragging = ref(false) // WHAT: Tracks drag-over styling state for drop zone
const selectedFile = ref<File | null>(null) // WHAT: User-selected file reference
const fileInput = ref<HTMLInputElement | null>(null) // WHAT: Hidden input reference for programmatic reset

// Import options
const sellerName = ref('') // WHAT: Seller name used for backend processing
const tradeName = ref('') // WHAT: Optional trade label override supplied by user
const autoCreate = ref(true) // WHAT: Checkbox state instructing backend to create seller/trade if missing
const dryRun = ref(false) // WHAT: Checkbox state toggling preview-only mode
const sellerOptions = ref<SellerOption[]>([]) // WHAT: Cached list of seller dropdown options
const selectedSellerId = ref<number | 'manual'>('manual') // WHAT: Currently chosen seller id or manual flag
const sellersLoading = ref(false) // WHAT: Loading indicator while fetching seller options
const sellersError = ref('') // WHAT: Error message to surface when seller fetch fails

// Processing state
const processingMessage = ref('Uploading file and analyzing columns...') // WHAT: Status text displayed during import
const importSuccess = ref(false) // WHAT: Tracks whether backend reported success
const importResults = ref('') // WHAT: Success payload provided by backend
const importError = ref('') // WHAT: Error payload provided by backend

/**
 * WHAT: Apply dropdown selection to local state and auto-create toggle.
 * WHY: Ensures manual entry clears sellerName while existing selections populate it.
 */
const applySellerSelection = (nextValue: number | 'manual'): void => {
  if (nextValue === 'manual') {
    sellerName.value = ''
    autoCreate.value = true
    return
  }
  const match = sellerOptions.value.find((option) => option.id === nextValue)
  sellerName.value = match?.name ?? ''
  autoCreate.value = false
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
    const response = await axios.get<SellerOption[]>('/api/acq/sellers/')
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

// WHAT: React to dropdown changes to keep sellerName/autoCreate synced.
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
 * Start import process
 */
async function startImport() {
  if (!selectedFile.value || !sellerName.value) return

  step.value = 'processing'
  processingMessage.value = 'Uploading file and analyzing columns...'

  try {
    // Create form data
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('seller_name', sellerName.value)
    if (tradeName.value) formData.append('trade_name', tradeName.value)
    formData.append('auto_create', autoCreate.value.toString())
    formData.append('dry_run', dryRun.value.toString())

    // Call backend API endpoint (to be created)
    const response = await axios.post('/api/acq/import-seller-tape/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    // Success
    step.value = 'results'
    importSuccess.value = true
    importResults.value = response.data.message || 'Import completed successfully!'
    emit('success')
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
 * Reset modal to initial state
 */
function resetModal() {
  step.value = 'upload'
  selectedFile.value = null
  sellerName.value = ''
  tradeName.value = ''
  autoCreate.value = true
  dryRun.value = false
  importSuccess.value = false
  importResults.value = ''
  importError.value = ''
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
</style>
