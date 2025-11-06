<template>
  <!-- Create CRM Contact Modal -->
  <!-- WHAT: Reusable modal for creating new MasterCRM contacts of any type -->
  <!-- WHY: Avoid code duplication - single modal handles legal, servicer, agent, contractor, title company -->
  <!-- HOW: Accepts contactType prop, posts to appropriate endpoint based on type -->
  <div v-if="show" class="modal d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5); z-index: 1070;">
    <div class="modal-dialog modal-md">
      <div class="modal-content">
        <div class="modal-header">
          <h6 class="modal-title">{{ modalTitle }}</h6>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <!-- Form fields for CRM contact -->
          <div class="row g-3">
            <!-- Firm/Company Name -->
            <div class="col-12">
              <label class="form-label small text-muted">Firm/Company Name <span class="text-danger">*</span></label>
              <input 
                v-model="formData.firm" 
                type="text" 
                class="form-control" 
                :placeholder="firmPlaceholder"
                @keydown.enter="createContact"
              />
            </div>
            
            <!-- Contact Name -->
            <div class="col-12">
              <label class="form-label small text-muted">Contact Name</label>
              <input 
                v-model="formData.contact_name" 
                type="text" 
                class="form-control" 
                placeholder="John Smith"
                @keydown.enter="createContact"
              />
            </div>
            
            <!-- Email -->
            <div class="col-md-6">
              <label class="form-label small text-muted">Email</label>
              <input 
                v-model="formData.email" 
                type="email" 
                class="form-control" 
                placeholder="contact@example.com"
                @keydown.enter="createContact"
              />
            </div>
            
            <!-- Phone -->
            <div class="col-md-6">
              <label class="form-label small text-muted">Phone</label>
              <input 
                v-model="formData.phone" 
                type="text" 
                class="form-control" 
                placeholder="(555) 123-4567"
                @keydown.enter="createContact"
              />
            </div>
            
            <!-- City -->
            <div class="col-md-6">
              <label class="form-label small text-muted">City</label>
              <input 
                v-model="formData.city" 
                type="text" 
                class="form-control" 
                placeholder="Phoenix"
                @keydown.enter="createContact"
              />
            </div>
            
            <!-- States (Multi-select) -->
            <div class="col-md-6">
              <label class="form-label small text-muted">State(s)</label>
              <input 
                v-model="statesInput" 
                type="text" 
                class="form-control" 
                placeholder="AZ, CA, TX"
                @keydown.enter="createContact"
              />
              <small class="form-text text-muted">Enter state codes separated by commas</small>
            </div>
            
            <!-- Notes (optional, for some contact types) -->
            <div v-if="showNotes" class="col-12">
              <label class="form-label small text-muted">Notes</label>
              <textarea 
                v-model="formData.notes" 
                class="form-control" 
                rows="2" 
                placeholder="Additional notes..."
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary btn-sm" @click="closeModal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-primary btn-sm" 
            :disabled="isCreating || !isValid" 
            @click="createContact"
          >
            <span v-if="!isCreating">Create Contact</span>
            <span v-else>
              <i class="fas fa-spinner fa-spin me-1"></i>Creating...
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import http from '@/lib/http'

// WHAT: Component props
// WHY: Control modal visibility and specify which type of contact to create
// HOW: show controls modal display, contactType determines endpoint and validation
const props = withDefaults(defineProps<{
  show: boolean
  contactType: 'legal' | 'servicer' | 'agent' | 'contractor' | 'title_company'
}>(), {
  show: false
})

// WHAT: Component emits
// WHY: Notify parent when modal closes or contact is successfully created
// HOW: Emit 'close' to hide modal, 'created' with CRM ID when contact is saved
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'created', crmId: number): void
}>()

// WHAT: Form data for new CRM contact
// WHY: Collect all contact information for submission
// HOW: Reactive ref object with all MasterCRM fields
const formData = ref<{
  firm: string
  contact_name: string
  email: string
  phone: string
  city: string
  notes: string
}>({
  firm: '',
  contact_name: '',
  email: '',
  phone: '',
  city: '',
  notes: ''
})

// WHAT: States input as comma-separated string
// WHY: Easier UX than multi-select dropdown for state codes
// HOW: Parse comma-separated string into array before submission
const statesInput = ref<string>('')

// WHAT: Creating state flag
// WHY: Disable submit button and show loading indicator during API call
// HOW: Set to true during createContact, false on completion or error
const isCreating = ref(false)

// WHAT: Compute modal title based on contact type
// WHY: Show appropriate title for each contact type
// HOW: Map contactType to human-readable label
const modalTitle = computed(() => {
  const titles: Record<typeof props.contactType, string> = {
    legal: 'New Legal Contact',
    servicer: 'New Servicer Contact',
    agent: 'New Agent Contact',
    contractor: 'New Contractor Contact',
    title_company: 'New Title Company Contact'
  }
  return titles[props.contactType] || 'New Contact'
})

// WHAT: Compute firm placeholder based on contact type
// WHY: Provide helpful context-specific placeholder text
// HOW: Map contactType to example firm name
const firmPlaceholder = computed(() => {
  const placeholders: Record<typeof props.contactType, string> = {
    legal: 'Law Firm Name',
    servicer: 'Servicing Company Name',
    agent: 'Real Estate Agency',
    contractor: 'Construction Company',
    title_company: 'Title Company Name'
  }
  return placeholders[props.contactType] || 'Company Name'
})

// WHAT: Determine if notes field should be shown
// WHY: Some contact types may benefit from notes field
// HOW: Show for all types currently, can be customized per type
const showNotes = computed(() => {
  return true // Show notes for all contact types
})

// WHAT: Validate form data
// WHY: Ensure at least firm is provided before allowing submission
// HOW: Check that firm field has content
const isValid = computed(() => {
  return formData.value.firm.trim().length > 0
})

// WHAT: Get API endpoint based on contact type
// WHY: Different contact types post to different CRM endpoints
// HOW: Map contactType to appropriate /core/crm/ endpoint
const apiEndpoint = computed(() => {
  const endpoints: Record<typeof props.contactType, string> = {
    legal: '/core/crm/legal/',
    servicer: '/core/crm/servicers/',
    agent: '/core/crm/', // Generic endpoint with tag
    contractor: '/core/crm/', // Generic endpoint with tag
    title_company: '/core/crm/' // Generic endpoint with tag
  }
  return endpoints[props.contactType]
})

// WHAT: Determine if we need to manually set tag in payload
// WHY: Some endpoints auto-set tag (legal, servicer), others need explicit tag
// HOW: Return true for agent, contractor, title_company
const needsManualTag = computed(() => {
  return ['agent', 'contractor', 'title_company'].includes(props.contactType)
})

/**
 * WHAT: Create new CRM contact
 * WHY: Save contact to backend and notify parent for assignment
 * HOW: POST to appropriate endpoint, emit 'created' with new ID, reset form
 */
async function createContact() {
  if (!isValid.value || isCreating.value) return
  
  try {
    isCreating.value = true
    
    // WHAT: Build payload with only non-empty fields
    // WHY: Cleaner API calls, MasterCRM fields are all nullable
    // HOW: Only include fields with content
    const payload: any = {}
    
    if (formData.value.firm.trim()) {
      payload.firm = formData.value.firm.trim()
    }
    if (formData.value.contact_name.trim()) {
      payload.contact_name = formData.value.contact_name.trim()
    }
    if (formData.value.email.trim()) {
      payload.email = formData.value.email.trim()
    }
    if (formData.value.phone.trim()) {
      payload.phone = formData.value.phone.trim()
    }
    if (formData.value.city.trim()) {
      payload.city = formData.value.city.trim()
    }
    if (formData.value.notes.trim()) {
      payload.notes = formData.value.notes.trim()
    }
    
    // WHAT: Parse states input into array
    // WHY: Backend expects states as array of 2-letter codes
    // HOW: Split on comma, trim, uppercase, filter empties
    if (statesInput.value.trim()) {
      const states = statesInput.value
        .split(',')
        .map(s => s.trim().toUpperCase())
        .filter(s => s.length === 2)
      if (states.length > 0) {
        payload.states = states
      }
    }
    
    // WHAT: Add tag for endpoints that require manual tag setting
    // WHY: Some endpoints (legal, servicer) auto-set tag; others need it explicitly
    // HOW: Check needsManualTag computed property
    if (needsManualTag.value) {
      payload.tag = props.contactType
    }
    
    console.log('Creating CRM contact:', { type: props.contactType, payload })
    
    // WHAT: POST to appropriate CRM endpoint
    // WHY: Create new MasterCRM record with correct tag
    // HOW: Use computed apiEndpoint based on contactType
    const response = await http.post(apiEndpoint.value, payload)
    
    console.log('CRM contact created:', response.data)
    
    // WHAT: Emit created event with new contact ID
    // WHY: Parent can auto-assign the newly created contact
    // HOW: Pass response.data.id to parent via emit
    emit('created', response.data.id)
    
    // WHAT: Reset form and close modal
    // WHY: Clean state for next use
    // HOW: Call resetForm and closeModal
    resetForm()
    closeModal()
    
  } catch (err: any) {
    console.error('Failed to create CRM contact:', err)
    console.error('Error response:', err.response?.data)
    console.error('Error status:', err.response?.status)
    
    // WHAT: Show detailed error message
    // WHY: Help user understand what went wrong
    // HOW: Extract error detail from response or show generic message
    const errorMsg = err.response?.data?.detail 
      || err.response?.data?.error
      || JSON.stringify(err.response?.data)
      || err.message 
      || 'Unknown error occurred'
    
    alert(`Failed to create contact:\n\n${errorMsg}\n\nCheck console for details.`)
  } finally {
    isCreating.value = false
  }
}

/**
 * WHAT: Reset form to initial empty state
 * WHY: Clear all fields when modal closes or after successful creation
 * HOW: Set all formData fields to empty strings
 */
function resetForm() {
  formData.value = {
    firm: '',
    contact_name: '',
    email: '',
    phone: '',
    city: '',
    notes: ''
  }
  statesInput.value = ''
}

/**
 * WHAT: Close modal and notify parent
 * WHY: Hide modal and reset form state
 * HOW: Emit 'close' event to parent, parent controls show prop
 */
function closeModal() {
  emit('close')
  // Reset form after a short delay to avoid visual glitch
  setTimeout(resetForm, 300)
}

// WHAT: Watch show prop to reset form when modal opens
// WHY: Ensure form is clean each time modal is displayed
// HOW: Watch show prop, reset form when it becomes true
watch(() => props.show, (newVal) => {
  if (newVal) {
    resetForm()
  }
})
</script>

<style scoped>
/* WHAT: Modal backdrop styling */
/* WHY: Ensure modal appears above other content */
/* HOW: Use high z-index and dark semi-transparent background */
.modal.d-block {
  display: block;
}
</style>

