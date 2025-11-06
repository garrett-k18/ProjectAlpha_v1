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
                  <label class="form-label">Trading Partner</label>
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
import { ref, watch, onMounted } from 'vue'
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
    // Populate form if editing
    if (props.editingOffer) {
      populateFormWithOffer(props.editingOffer)
    }
  } else {
    resetForm()
  }
})

// WHAT: Populate form with existing offer data
// WHY: Pre-fill form when editing an offer
function populateFormWithOffer(offer: any) {
  formData.value = {
    offer_price: offer.offer_price?.toString() || '',
    offer_date: offer.offer_date || '',
    buyer_name: offer.buyer_name || '',
    buyer_agent: offer.buyer_agent || '',
    financing_type: offer.financing_type || '',
    offer_status: offer.offer_status || '',
    seller_credits: offer.seller_credits?.toString() || '',
    trading_partner: offer.trading_partner || null,
    notes: offer.notes || ''
  }
}

// WHAT: Initialize trading partners if note sale
// WHY: Need trading partner dropdown options
const tradingPartnersStore = useTradingPartnersStore()

// WHAT: Initialize and cleanup on mount/unmount
// WHY: Proper lifecycle management
onMounted(async () => {
  if (isNoteSale) {
    // Load trading partners for dropdown
    await tradingPartnersStore.fetchTradingPartners()
    tradingPartners.value = tradingPartnersStore.results
  }
})

// WHAT: Close modal and notify parent
// WHY: Update parent state and clean up form
function closeModal() {
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
