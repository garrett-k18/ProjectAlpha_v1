<template>
  <!-- WHAT: Modal for adding/editing REO scopes/bids -->
  <!-- WHY: Centralized form for scope management -->
  <!-- WHERE: Used by ReoScopesSection component -->
  <div v-if="modelValue" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">{{ isEditing ? 'Edit' : 'Add' }} Scope ({{ taskTypeLabel }})</h6>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <!-- Vendor selection -->
            <div class="col-12">
              <label class="form-label small text-muted">Choose Vendor</label>
              <div class="d-flex gap-2">
                <select
                  v-model="form.crm"
                  class="form-select form-select-sm"
                  :style="{ flex: '0 0 80%', maxWidth: '80%' }"
                >
                  <option :value="null">-- Select existing vendor --</option>
                  <option v-for="v in vendorOptions" :key="v.id" :value="v.id">
                    {{ v.firm || 'Unknown' }}
                    <span v-if="v.contact_name"> ({{ v.contact_name }})</span>
                  </option>
                </select>
                <button type="button" class="btn btn-outline-secondary btn-sm" @click="openVendorModal">
                  <i class="fas fa-user-plus me-1"></i> New Vendor
                </button>
              </div>
            </div>

            <!-- Dates and totals -->
            <div class="col-md-6">
              <label class="form-label small text-muted">Bid Date</label>
              <input 
                ref="scopeDateInput"
                type="text" 
                class="form-control form-control-sm date" 
                data-toggle="date-picker" 
                data-single-date-picker="true" 
                :value="convertToDisplayDate(form.scope_date)"
                @input="handleScopeDateInput"
                placeholder="Select date (optional)" 
                spellcheck="false"
              />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Expected Completion</label>
              <input 
                ref="completionDateInput"
                type="text" 
                class="form-control form-control-sm date" 
                data-toggle="date-picker" 
                data-single-date-picker="true" 
                :value="convertToDisplayDate(form.expected_completion)"
                @input="handleCompletionDateInput"
                placeholder="Select date (optional)" 
                spellcheck="false"
              />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Total Cost</label>
              <UiCurrencyInput 
                v-model="form.total_cost"
                prefix="$"
                size="sm"
                placeholder="0.00"
              />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Notes</label>
              <textarea v-model="form.notes" rows="3" class="form-control" placeholder="Itemization or notes..."></textarea>
            </div>
            
            <!-- Document Upload -->
            <div class="col-12">
              <label class="form-label small text-muted">Upload Documents</label>
              <input 
                ref="fileInput"
                type="file" 
                class="form-control form-control-sm" 
                multiple
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                @change="handleFileUpload"
              />
              <div class="form-text">Accepted formats: PDF, DOC, DOCX, JPG, PNG (will be wired to database later)</div>
              
              <!-- File List -->
              <div v-if="uploadedFiles.length > 0" class="mt-2">
                <div class="small fw-bold mb-1">Selected Files:</div>
                <div 
                  v-for="(file, index) in uploadedFiles" 
                  :key="index"
                  class="d-flex align-items-center justify-content-between bg-light p-2 rounded mb-1"
                >
                  <div class="d-flex align-items-center gap-2">
                    <i class="fas fa-file-alt text-muted"></i>
                    <span class="small">{{ file.name }}</span>
                    <span class="badge bg-secondary">{{ formatFileSize(file.size) }}</span>
                  </div>
                  <button 
                    type="button" 
                    class="btn btn-sm btn-outline-danger" 
                    @click="removeFile(index)"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button type="button" class="btn btn-primary" :disabled="submitting || !form.crm" @click="submit">
            <span v-if="!submitting"><i class="fas fa-save me-1"></i> Save</span>
            <span v-else>Saving...</span>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- New Vendor Modal -->
  <div v-if="showVendorModal" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5); z-index: 1060;">
    <div class="modal-dialog modal-md">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">New Vendor (MasterCRM)</h6>
          <button type="button" class="btn-close" @click="showVendorModal = false"></button>
        </div>
        <div class="modal-body">
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label small text-muted">Company</label>
              <input v-model="newVendor.firm" type="text" class="form-control" placeholder="ACME Construction" />
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">Contact Name</label>
              <input v-model="newVendor.name" type="text" class="form-control" placeholder="Jane Smith" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Email</label>
              <input v-model="newVendor.email" type="email" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">Phone</label>
              <input v-model="newVendor.phone" type="text" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">City</label>
              <input v-model="newVendor.city" type="text" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label small text-muted">State</label>
              <input v-model="newVendor.state" type="text" maxlength="2" class="form-control" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="showVendorModal = false">Cancel</button>
          <button type="button" class="btn btn-primary" :disabled="creatingVendor || !newVendor.firm" @click="createVendor">
            <span v-if="!creatingVendor">Create</span>
            <span v-else>Creating...</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import http from '@/lib/http'
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'

// WHAT: Component props
// WHY: Receive modal state, hub/task info, and editing scope
interface Props {
  modelValue: boolean
  hubId: number
  taskId: number
  taskType: 'trashout' | 'renovation'
  editingScope?: any | null
}

const props = withDefaults(defineProps<Props>(), {
  editingScope: null
})

// WHAT: Component emits
// WHY: Notify parent of modal state changes and scope actions
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'scope-added'): void
  (e: 'scope-updated'): void
}>()

// WHAT: Refs for date picker inputs and file input
// WHY: Initialize date pickers on mount and handle file uploads
const scopeDateInput = ref<HTMLInputElement | null>(null)
const completionDateInput = ref<HTMLInputElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// WHAT: Form state
// WHY: Store scope data for create/update
const form = ref<{
  crm: number | null
  scope_date: string | null
  total_cost: string | null
  expected_completion: string | null
  notes: string | null
}>({
  crm: null,
  scope_date: null,
  total_cost: null,
  expected_completion: null,
  notes: null
})

// WHAT: File upload state
// WHY: Track selected files for upload
const uploadedFiles = ref<File[]>([])

// WHAT: Modal and vendor state
// WHY: Manage modal visibility and vendor creation
const submitting = ref(false)
const vendorOptions = ref<Array<{ id: number; firm: string | null; contact_name: string | null }>>([])
const showVendorModal = ref(false)
const creatingVendor = ref(false)
const newVendor = ref<{
  firm: string | null
  name: string | null
  email: string | null
  phone: string | null
  city: string | null
  state: string | null
}>({
  firm: null,
  name: null,
  email: null,
  phone: null,
  city: null,
  state: null
})

// WHAT: Computed properties
// WHY: Determine edit mode and task type label
const isEditing = computed(() => props.editingScope != null)
const taskTypeLabel = computed(() => props.taskType === 'trashout' ? 'Trashout' : 'Renovation')

// WHAT: Load vendors for dropdown
// WHY: Populate vendor selection options
async function loadVendors() {
  try {
    const res = await http.get('/acq/brokers/?tag=vendor')
    const data = res.data
    const results = (data?.results || data || []) as any[]
    vendorOptions.value = results.map((crm: any) => ({
      id: crm.id,
      firm: crm.firm || null,
      contact_name: crm.name || crm.contact_name || null
    }))
  } catch (e) {
    console.error('Failed to load vendors:', e)
    vendorOptions.value = []
  }
}

// WHAT: Open vendor creation modal
// WHY: Allow adding new vendors inline
function openVendorModal() {
  showVendorModal.value = true
}

// WHAT: Create new vendor
// WHY: Add vendor to CRM and preselect in form
async function createVendor() {
  creatingVendor.value = true
  try {
    const payload = { ...newVendor.value, tag: 'vendor' }
    const res = await http.post('/acq/brokers/', payload)
    const v = res.data
    
    // Add to options and preselect
    vendorOptions.value.unshift({
      id: v.id,
      firm: v.firm || null,
      contact_name: v.name || v.contact_name || null
    })
    form.value.crm = v.id
    showVendorModal.value = false
    
    // Reset vendor form
    newVendor.value = {
      firm: null,
      name: null,
      email: null,
      phone: null,
      city: null,
      state: null
    }
  } catch (e) {
    console.error('Failed to create vendor:', e)
    alert('Failed to create vendor. Please try again.')
  } finally {
    creatingVendor.value = false
  }
}

// WHAT: Submit form (create or update)
// WHY: Save scope data to backend
async function submit() {
  submitting.value = true
  try {
    const payload = {
      asset_hub_id: props.hubId,
      scope_kind: props.taskType,
      reo_task: props.taskId,
      crm: form.value.crm,
      scope_date: form.value.scope_date,
      total_cost: form.value.total_cost,
      expected_completion: form.value.expected_completion,
      notes: form.value.notes
    }

    if (isEditing.value) {
      // Update existing scope
      await http.patch(`/am/outcomes/reo-scopes/${props.editingScope.id}/`, payload)
      emit('scope-updated')
    } else {
      // Create new scope
      await http.post('/am/outcomes/reo-scopes/', payload)
      emit('scope-added')
    }
    
    // TODO: Handle file uploads when document database is wired
    if (uploadedFiles.value.length > 0) {
      console.log('Files to upload (not yet wired):', uploadedFiles.value.map(f => f.name))
      // File upload implementation will go here
    }
    
    closeModal()
  } catch (err: any) {
    console.error('Failed to save scope:', err)
    alert('Failed to save scope. Please try again.')
  } finally {
    submitting.value = false
  }
}

// WHAT: Handle file upload selection
// WHY: Allow users to attach documents to scopes
function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const newFiles = Array.from(target.files)
    uploadedFiles.value = [...uploadedFiles.value, ...newFiles]
  }
}

// WHAT: Remove a selected file
// WHY: Allow users to remove unwanted files before upload
function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

// WHAT: Format file size for display
// WHY: Show human-readable file sizes
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// WHAT: Close modal
// WHY: Reset state and notify parent
function closeModal() {
  emit('update:modelValue', false)
  submitting.value = false
  
  // Reset form
  form.value = {
    crm: null,
    scope_date: null,
    total_cost: null,
    expected_completion: null,
    notes: null
  }
  
  // Reset files
  uploadedFiles.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// WHAT: Convert US date format to backend format
// WHY: Backend expects yyyy-mm-dd but users see mm/dd/yyyy
function convertToBackendDate(usDate: string): string {
  if (!usDate) return ''
  try {
    const [month, day, year] = usDate.split('/')
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
  } catch {
    return usDate
  }
}

// WHAT: Convert backend date format to US display format
// WHY: Show users familiar mm/dd/yyyy format
function convertToDisplayDate(backendDate: string | null): string {
  if (!backendDate) return ''
  try {
    const [year, month, day] = backendDate.split('-')
    return `${month}/${day}/${year}`
  } catch {
    return backendDate
  }
}

// WHAT: Handle scope date input from text field
// WHY: Convert display format to backend format and save
function handleScopeDateInput(event: Event) {
  const target = event.target as HTMLInputElement
  const displayDate = target.value
  const backendDate = convertToBackendDate(displayDate)
  form.value.scope_date = backendDate
}

// WHAT: Handle completion date input from text field
// WHY: Convert display format to backend format and save
function handleCompletionDateInput(event: Event) {
  const target = event.target as HTMLInputElement
  const displayDate = target.value
  const backendDate = convertToBackendDate(displayDate)
  form.value.expected_completion = backendDate
}

// WHAT: Initialize Bootstrap date pickers
// WHY: Enable calendar popup for date selection
function initializeDatePickers() {
  // Check if jQuery and datepicker are available
  if (typeof $ === 'undefined' || typeof $.fn.datepicker === 'undefined') {
    console.warn('jQuery or datepicker not available')
    return
  }
  
  // Small delay to ensure DOM is ready
  setTimeout(() => {
    if (scopeDateInput.value) {
      try {
        $(scopeDateInput.value).datepicker({
          format: 'mm/dd/yyyy',
          autoclose: true,
          todayHighlight: true
        }).on('changeDate', (e: any) => {
          if (e.date) {
            const month = (e.date.getMonth() + 1).toString().padStart(2, '0')
            const day = e.date.getDate().toString().padStart(2, '0')
            const year = e.date.getFullYear()
            form.value.scope_date = `${year}-${month}-${day}`
          }
        })
      } catch (err) {
        console.error('Failed to initialize scope date picker:', err)
      }
    }
    
    if (completionDateInput.value) {
      try {
        $(completionDateInput.value).datepicker({
          format: 'mm/dd/yyyy',
          autoclose: true,
          todayHighlight: true
        }).on('changeDate', (e: any) => {
          if (e.date) {
            const month = (e.date.getMonth() + 1).toString().padStart(2, '0')
            const day = e.date.getDate().toString().padStart(2, '0')
            const year = e.date.getFullYear()
            form.value.expected_completion = `${year}-${month}-${day}`
          }
        })
      } catch (err) {
        console.error('Failed to initialize completion date picker:', err)
      }
    }
  }, 100)
}

// WHAT: Cleanup date pickers
// WHY: Prevent memory leaks
function cleanupDatePickers() {
  if (typeof $ === 'undefined' || typeof $.fn.datepicker === 'undefined') return
  
  try {
    if (scopeDateInput.value) {
      $(scopeDateInput.value).datepicker('destroy')
    }
  } catch (err) {
    // Ignore cleanup errors
  }
  
  try {
    if (completionDateInput.value) {
      $(completionDateInput.value).datepicker('destroy')
    }
  } catch (err) {
    // Ignore cleanup errors
  }
}

// WHAT: Watch for modal open
// WHY: Load vendors and populate form if editing
watch(() => props.modelValue, async (newVal) => {
  if (newVal) {
    loadVendors()
    
    // If editing, populate form
    if (props.editingScope) {
      form.value = {
        crm: props.editingScope.crm || null,
        scope_date: props.editingScope.scope_date || null,
        total_cost: props.editingScope.total_cost || null,
        expected_completion: props.editingScope.expected_completion || null,
        notes: props.editingScope.notes || null
      }
    }
    
    // Initialize date pickers after DOM updates
    await nextTick()
    initializeDatePickers()
  } else {
    cleanupDatePickers()
  }
})

// WHAT: Cleanup on component unmount
// WHY: Prevent memory leaks from date pickers
onBeforeUnmount(() => {
  cleanupDatePickers()
})
</script>

<style scoped>
/* WHAT: Modal z-index management */
/* WHY: Ensure vendor modal appears above scope modal */
.modal {
  z-index: 1055;
}
</style>
