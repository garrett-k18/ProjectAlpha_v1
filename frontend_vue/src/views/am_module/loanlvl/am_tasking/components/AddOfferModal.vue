<template>
  <!-- WHAT: Add Offer Modal -->
  <!-- WHY: Allow manual entry of offers with all required fields -->
  <div v-if="modelValue" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ props.editingOffer ? 'Edit Offer' : 'Add New Offer' }}</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitOffer">
            <div class="row g-3">
              <!-- Offer Price -->
              <div class="col-md-6">
                <label class="form-label">Offer Price *</label>
                <UiCurrencyInput 
                  v-model="formData.offer_price"
                  prefix="$"
                  size="sm"
                  placeholder="0.00"
                  required
                />
              </div>
              
              <!-- Offer Date -->
              <div class="col-md-6">
                <label class="form-label">Offer Date</label>
                <div class="form-control form-control-sm" style="border: 1px solid #dee2e6;">
                  <EditableDate
                    v-model="formData.offer_date"
                    placeholder="Select date (optional)"
                  />
                </div>
              </div>
              
              <!-- WHAT: Note Sale specific fields -->
              <!-- WHY: Note sales use trading partner instead of buyer -->
              <template v-if="isNoteSale">
                <!-- Trading Partner -->
                <div class="col-12">
                  <label class="form-label d-flex justify-content-between align-items-center">
                    <span>Trading Partner</span>
                    <button 
                      type="button" 
                      class="btn btn-xs btn-outline-primary d-inline-flex align-items-center gap-1"
                      style="font-size: 0.7rem; padding: 2px 8px;"
                      @click="showAddTradingPartner = true"
                    >
                      <i class="fas fa-plus"></i>
                      <span>Add New</span>
                    </button>
                  </label>
                  <select 
                    v-model="formData.trading_partner"
                    class="form-select form-select-sm"
                  >
                    <option :value="null">Select Trading Partner (optional)</option>
                    <option v-for="tp in tradingPartners" :key="tp.id" :value="tp.id">
                      {{ tp.firm || tp.name || `TP ${tp.id}` }}
                    </option>
                  </select>
                </div>
                
                <!-- WHAT: Inline Trading Partner creation form -->
                <!-- WHY: Allow quick creation without leaving modal -->
                <div v-if="showAddTradingPartner" class="col-12">
                  <div class="card border-primary">
                    <div class="card-header bg-primary-subtle py-2">
                      <div class="d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">Add New Trading Partner</h6>
                        <button 
                          type="button" 
                          class="btn-close btn-sm" 
                          @click="cancelAddTradingPartner"
                        ></button>
                      </div>
                    </div>
                    <div class="card-body">
                      <div class="row g-2">
                        <div class="col-md-6">
                          <label class="form-label small">Firm Name</label>
                          <input 
                            v-model="newTradingPartner.firm"
                            type="text" 
                            class="form-control form-control-sm" 
                            placeholder="Enter firm name"
                          />
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small">Contact Name</label>
                          <input 
                            v-model="newTradingPartner.contact_name"
                            type="text" 
                            class="form-control form-control-sm" 
                            placeholder="Enter contact name"
                          />
                        </div>
                        <div class="col-12">
                          <small class="text-muted fst-italic">* At least firm name or contact name is recommended</small>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small">Email</label>
                          <input 
                            v-model="newTradingPartner.email"
                            type="email" 
                            class="form-control form-control-sm" 
                            placeholder="contact@firm.com"
                          />
                        </div>
                        <div class="col-md-6">
                          <label class="form-label small">Phone</label>
                          <input 
                            v-model="newTradingPartner.phone"
                            type="tel" 
                            class="form-control form-control-sm" 
                            placeholder="(555) 123-4567"
                          />
                        </div>
                        <div class="col-12 d-flex justify-content-end gap-2 mt-2">
                          <button 
                            type="button" 
                            class="btn btn-sm btn-light"
                            @click="cancelAddTradingPartner"
                          >
                            Cancel
                          </button>
                          <button 
                            type="button" 
                            class="btn btn-sm btn-primary"
                            @click="saveTradingPartner"
                            :disabled="isSavingTradingPartner || (!newTradingPartner.firm && !newTradingPartner.contact_name)"
                          >
                            <span v-if="isSavingTradingPartner" class="spinner-border spinner-border-sm me-1"></span>
                            {{ isSavingTradingPartner ? 'Saving...' : 'Save' }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </template>
              
              <!-- WHAT: Property sale specific fields -->
              <!-- WHY: Property sales need buyer and financing details -->
              <template v-else>
                <!-- Buyer Name -->
                <div class="col-md-6">
                  <label class="form-label">Buyer Name</label>
                  <input 
                    v-model="formData.buyer_name"
                    type="text" 
                    class="form-control form-control-sm" 
                    placeholder="Enter buyer name (optional)"
                  />
                </div>
                
                <!-- Buyer Agent -->
                <div class="col-md-6">
                  <label class="form-label">Buyer Agent</label>
                  <input 
                    v-model="formData.buyer_agent"
                    type="text" 
                    class="form-control form-control-sm" 
                    placeholder="Enter agent name (optional)"
                  />
                </div>
                
                <!-- Financing Type -->
                <div class="col-md-6">
                  <label class="form-label">Financing Type</label>
                  <select 
                    v-model="formData.financing_type"
                    class="form-select form-select-sm"
                  >
                    <option value="">Select financing type (optional)</option>
                    <option value="cash">Cash</option>
                    <option value="conventional">Conventional Financing</option>
                    <option value="fha">FHA Financing</option>
                    <option value="va">VA Financing</option>
                    <option value="usda">USDA Financing</option>
                    <option value="hard_money">Hard Money</option>
                    <option value="other">Other Financing</option>
                  </select>
                </div>
                
                <!-- Seller Credits -->
                <div class="col-md-6">
                  <label class="form-label">Seller Credits</label>
                  <UiCurrencyInput 
                    v-model="formData.seller_credits"
                    prefix="$"
                    size="sm"
                    placeholder="0.00"
                  />
                </div>
              </template>
              
              <!-- Offer Status (shown for all offer types) -->
              <div class="col-md-6">
                <label class="form-label">Offer Status</label>
                <select 
                  v-model="formData.offer_status"
                  class="form-select form-select-sm"
                >
                  <option value="">Select status (optional)</option>
                  <option value="pending">Pending</option>
                  <option value="accepted">Accepted</option>
                  <option value="rejected">Rejected</option>
                  <option value="countered">Countered</option>
                  <option value="withdrawn">Withdrawn</option>
                </select>
              </div>
              
              <!-- Document Upload -->
              <div class="col-12">
                <label class="form-label">Upload Documents</label>
                <input 
                  ref="fileInput"
                  type="file" 
                  class="form-control form-control-sm" 
                  multiple
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  @change="handleFileUpload"
                />
                <div class="form-text">Accepted formats: PDF, DOC, DOCX, JPG, PNG</div>
                
                <!-- File List -->
                <div v-if="uploadedFiles.length > 0" class="mt-2">
                  <div class="small fw-bold mb-1">Selected Files:</div>
                  <div 
                    v-for="(file, index) in uploadedFiles" 
                    :key="index"
                    class="d-flex align-items-center justify-content-between bg-light p-2 rounded mb-1"
                  >
                    <span class="small">{{ file.name }}</span>
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
              
              <!-- Notes -->
              <div class="col-12">
                <label class="form-label">Notes</label>
                <textarea 
                  v-model="formData.notes"
                  class="form-control form-control-sm" 
                  rows="3"
                  placeholder="Additional notes about this offer..."
                ></textarea>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="submitOffer" :disabled="isSubmitting">
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2"></span>
            {{ isSubmitting ? (props.editingOffer ? 'Updating...' : 'Adding...') : (props.editingOffer ? 'Update Offer' : 'Add Offer') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import http from '@/lib/http'
import UiCurrencyInput from '@/components/ui/UiCurrencyInput.vue'
import EditableDate from '@/components/ui/EditableDate.vue'
import { useTradingPartnersStore } from '@/stores/tradingPartners'

// WHAT: Component props
// WHY: Receive modal state and asset hub ID from parent
interface Props {
  modelValue: boolean
  hubId: number
  editingOffer?: any
  offerSource?: 'short_sale' | 'reo' | 'note_sale'
}

// WHAT: Component emits
// WHY: Communicate with parent component
interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'offer-added'): void
  (e: 'offer-updated'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// WHAT: Check if this is a note sale offer
// WHY: Note sales have different fields than property sales
const isNoteSale = props.offerSource === 'note_sale'

// WHAT: Form state and file handling
// WHY: Manage modal form data and file uploads
const isSubmitting = ref(false)
const uploadedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

// WHAT: Trading partners list for note sale offers
// WHY: Allow selection of trading partner who made the offer
const tradingPartners = ref<any[]>([])

// WHAT: Inline trading partner creation state
// WHY: Allow adding new trading partners without leaving modal
const showAddTradingPartner = ref(false)
const isSavingTradingPartner = ref(false)
const newTradingPartner = ref({
  firm: '',
  contact_name: '',
  email: '',
  phone: ''
})

// WHAT: Form data structure
// WHY: Store all offer fields with default values
const formData = ref({
  offer_price: '',
  offer_date: '',
  buyer_name: '',
  buyer_agent: '',
  financing_type: '',
  offer_status: '',
  seller_credits: '',
  trading_partner: null as number | null,
  notes: ''
})

// WHAT: Reset form when modal opens/closes
// WHY: Ensure clean state for each new offer
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    // Load trading partners if note sale
    if (isNoteSale && tradingPartners.value.length === 0) {
      await tradingPartnersStore.fetchTradingPartners()
      tradingPartners.value = tradingPartnersStore.results
    }
    
    // WHAT: Use nextTick to ensure DOM is ready before populating
    // WHY: Some components need to be mounted before they can receive values
    await nextTick()
    
    // Populate form if editing (after reset and nextTick)
    if (props.editingOffer) {
      console.log('Populating form with offer:', props.editingOffer)
      populateFormWithOffer(props.editingOffer)
    } else {
      // Only reset if not editing
      resetForm()
    }
  }
})

// WHAT: Watch editingOffer changes
// WHY: Update form when different offer is selected for editing
watch(() => props.editingOffer, async (newOffer) => {
  if (newOffer && props.modelValue) {
    console.log('EditingOffer changed:', newOffer)
    await nextTick()
    populateFormWithOffer(newOffer)
  }
}, { deep: true })

// WHAT: Populate form with existing offer data
// WHY: Pre-fill form when editing an offer
function populateFormWithOffer(offer: any) {
  console.log('Populating form with data:', {
    offer_price: offer.offer_price,
    offer_date: offer.offer_date,
    buyer_name: offer.buyer_name,
    trading_partner: offer.trading_partner,
    offer_status: offer.offer_status
  })
  
  formData.value.offer_price = offer.offer_price?.toString() || ''
  formData.value.offer_date = offer.offer_date || ''
  formData.value.buyer_name = offer.buyer_name || ''
  formData.value.buyer_agent = offer.buyer_agent || ''
  formData.value.financing_type = offer.financing_type || ''
  formData.value.offer_status = offer.offer_status || ''
  formData.value.seller_credits = offer.seller_credits?.toString() || ''
  formData.value.trading_partner = offer.trading_partner || null
  formData.value.notes = offer.notes || ''
  
  console.log('Form data after population:', formData.value)
}

// WHAT: Initialize trading partners if note sale
// WHY: Need trading partner dropdown options
const tradingPartnersStore = useTradingPartnersStore()

// WHAT: Initialize and cleanup on mount/unmount
// WHY: Proper lifecycle management
onMounted(async () => {
  if (isNoteSale) {
    // Load trading partners for dropdown
    await loadTradingPartners()
  }
})

// WHAT: Load trading partners from store/API
// WHY: Populate dropdown with current trading partners
async function loadTradingPartners() {
  await tradingPartnersStore.fetchPartners()
  tradingPartners.value = tradingPartnersStore.results
}

// WHAT: Cancel adding new trading partner
// WHY: Reset form and hide inline creation UI
function cancelAddTradingPartner() {
  showAddTradingPartner.value = false
  newTradingPartner.value = {
    firm: '',
    contact_name: '',
    email: '',
    phone: ''
  }
}

// WHAT: Save new trading partner to backend
// WHY: Create trading partner and add to dropdown
async function saveTradingPartner() {
  // WHAT: Validate that at least firm is provided for usability
  // WHY: Trading partner without any identifier isn't useful
  if (!newTradingPartner.value.firm && !newTradingPartner.value.contact_name) {
    alert('Please enter at least a firm name or contact name.')
    return
  }
  
  try {
    isSavingTradingPartner.value = true
    
    // WHAT: Prepare minimal payload - only send fields that have values
    // WHY: All MasterCRM fields are nullable/optional, cleaner to omit empty fields
    const payload: any = {}
    
    if (newTradingPartner.value.firm) {
      payload.firm = newTradingPartner.value.firm
    }
    if (newTradingPartner.value.contact_name) {
      payload.contact_name = newTradingPartner.value.contact_name
    }
    if (newTradingPartner.value.email) {
      payload.email = newTradingPartner.value.email
    }
    if (newTradingPartner.value.phone) {
      payload.phone = newTradingPartner.value.phone
    }
    
    console.log('Creating trading partner with payload:', payload)
    
    // WHAT: POST to trading partners endpoint
    // WHY: Create new MasterCRM record with trading_partner tag (auto-set by serializer)
    const response = await http.post('/core/crm/trading-partners/', payload)
    
    console.log('Trading partner created:', response.data)
    
    // WHAT: Reload trading partners list
    // WHY: Include newly created trading partner in dropdown
    await loadTradingPartners()
    
    // WHAT: Auto-select the newly created trading partner
    // WHY: UX convenience - they probably want to use the one they just created
    formData.value.trading_partner = response.data.id
    
    // WHAT: Hide inline form and reset
    cancelAddTradingPartner()
    
  } catch (err: any) {
    console.error('Failed to create trading partner:', err)
    console.error('Error response data:', err.response?.data)
    console.error('Error status:', err.response?.status)
    
    // WHAT: Show detailed error message to user
    // WHY: Help diagnose what went wrong
    const errorMsg = err.response?.data?.detail 
      || err.response?.data?.error
      || JSON.stringify(err.response?.data)
      || err.message 
      || 'Unknown error occurred'
    
    alert(`Failed to create trading partner:\n\n${errorMsg}\n\nCheck console for details.`)
  } finally {
    isSavingTradingPartner.value = false
  }
}

// WHAT: Close modal and notify parent
// WHY: Update parent state and clean up form
function closeModal() {
  resetForm()
  emit('update:modelValue', false)
}

// WHAT: Reset form to initial state
// WHY: Clear all data when modal is closed or after submission
function resetForm() {
  formData.value = {
    offer_price: '',
    offer_date: '',
    buyer_name: '',
    buyer_agent: '',
    financing_type: '',
    offer_status: '',
    seller_credits: '',
    trading_partner: null,
    notes: ''
  }
  uploadedFiles.value = []
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// WHAT: Handle file upload selection
// WHY: Allow users to attach documents to offers
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

// WHAT: Submit new offer to backend
// WHY: Save offer data and upload documents
async function submitOffer() {
  if (isSubmitting.value) return
  
  try {
    isSubmitting.value = true
    
    // Validate required fields - only offer_price is required
    if (!formData.value.offer_price) {
      alert('Please enter an offer price.')
      return
    }
    
    // Prepare offer data
    const offerData: any = {
      asset_hub_id: props.hubId,
      offer_source: props.offerSource || 'short_sale',
      offer_price: parseFloat(formData.value.offer_price) || 0,
      offer_date: formData.value.offer_date || null,
      offer_status: formData.value.offer_status || 'pending',
      notes: formData.value.notes || null
    }
    
    // WHAT: Add note sale specific fields
    // WHY: Note sales use trading partner, not buyer details
    if (isNoteSale) {
      offerData.trading_partner = formData.value.trading_partner || null
    } else {
      // WHAT: Add property sale specific fields
      // WHY: Property sales need buyer and financing details
      offerData.buyer_name = formData.value.buyer_name || null
      offerData.buyer_agent = formData.value.buyer_agent || null
      offerData.financing_type = formData.value.financing_type || null
      offerData.seller_credits = parseFloat(formData.value.seller_credits) || 0
    }
    
    console.log('Submitting offer:', offerData)
    
    let response
    if (props.editingOffer) {
      // Update existing offer
      response = await http.patch(`/am/outcomes/offers/${props.editingOffer.id}/`, offerData)
      console.log('Offer updated:', response.data)
      emit('offer-updated')
    } else {
      // Create new offer
      response = await http.post('/am/outcomes/offers/', offerData)
      console.log('Offer created:', response.data)
      emit('offer-added')
    }
    
    // TODO: Handle file uploads if any files are selected
    if (uploadedFiles.value.length > 0) {
      console.log('Files to upload:', uploadedFiles.value.map(f => f.name))
      // File upload implementation would go here
    }
    
    // Close modal
    closeModal()
    
  } catch (err: any) {
    console.error('Failed to submit offer:', err)
    console.error('Error response:', err.response?.data)
    alert('Failed to add offer. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

</script>
