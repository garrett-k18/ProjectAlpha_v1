<template>
  <!-- WHAT: Reusable offers section component -->
  <!-- WHY: Display and manage offers from various sources -->
  <div class="mt-3">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h6 class="mb-0 text-muted">Current Offers</h6>
      <button 
        type="button" 
        class="btn btn-sm btn-outline-primary"
        @click="showAddOfferModal = true"
      >
        <i class="fas fa-plus me-1"></i>
        Add Offer
      </button>
    </div>
    
    <!-- Offers list -->
    <div v-if="offers.length === 0" class="text-muted small text-center py-2">
      No offers received yet
    </div>
    <div v-else class="offers-list">
      <div 
        v-for="offer in offers.filter(o => o && o.id)" 
        :key="offer.id" 
        class="offer-item"
      >
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center flex-wrap gap-2 small ms-2">
            <strong class="text-dark">${{ formatOfferPrice(offer.offer_price) }}</strong>
            <!-- WHAT: Inline status dropdown for quick editing -->
            <!-- WHY: Allow status changes without opening full edit modal -->
            <div class="d-flex align-items-center gap-1">
              <span class="text-muted" style="font-size: 0.7rem;">Offer Status:</span>
              <div class="dropdown position-relative">
                <button 
                  class="btn btn-sm p-0 border-0" 
                  type="button" 
                  @click.stop="toggleStatusDropdown(offer.id)"
                  :title="'Click to change status'"
                >
                  <UiBadge :tone="getOfferStatusTone(offer.offer_status)" size="sm">
                    {{ formatOfferStatus(offer.offer_status) }}
                  </UiBadge>
                </button>
                <ul 
                  v-if="openStatusDropdownId === offer.id"
                  class="dropdown-menu show position-absolute p-2"
                  style="left: 0; top: 100%; z-index: 1050; min-width: 140px;"
                  @click.stop
                >
                  <li class="mb-1">
                    <button class="btn btn-sm w-100 p-0 border-0 text-start" type="button" @click="updateOfferStatus(offer.id, 'pending')">
                      <UiBadge tone="warning" size="sm" class="w-100">Pending</UiBadge>
                    </button>
                  </li>
                  <li class="mb-1">
                    <button class="btn btn-sm w-100 p-0 border-0 text-start" type="button" @click="updateOfferStatus(offer.id, 'accepted')">
                      <UiBadge tone="success" size="sm" class="w-100">Accepted</UiBadge>
                    </button>
                  </li>
                  <li class="mb-1">
                    <button class="btn btn-sm w-100 p-0 border-0 text-start" type="button" @click="updateOfferStatus(offer.id, 'rejected')">
                      <UiBadge tone="danger" size="sm" class="w-100">Rejected</UiBadge>
                    </button>
                  </li>
                  <li class="mb-1">
                    <button class="btn btn-sm w-100 p-0 border-0 text-start" type="button" @click="updateOfferStatus(offer.id, 'countered')">
                      <UiBadge tone="info" size="sm" class="w-100">Countered</UiBadge>
                    </button>
                  </li>
                  <li>
                    <button class="btn btn-sm w-100 p-0 border-0 text-start" type="button" @click="updateOfferStatus(offer.id, 'withdrawn')">
                      <UiBadge tone="secondary" size="sm" class="w-100">Withdrawn</UiBadge>
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <span v-if="offer.buyer_name" class="text-muted">{{ offer.buyer_name }}</span>
            <span v-if="offer.financing_type" class="text-muted">{{ formatFinancingType(offer.financing_type) }}</span>
            <span v-if="offer.seller_credits > 0" class="text-muted">${{ formatOfferPrice(offer.seller_credits) }} credits</span>
          </div>
          <div class="dropdown position-relative me-2">
            <button 
              class="btn btn-xs btn-outline-dark offer-menu-btn" 
              type="button" 
              @click="toggleDropdown(offer.id)"
            >
              ⋮
            </button>
            <ul 
              v-if="openDropdownId === offer.id"
              class="dropdown-menu show position-absolute"
              style="right: 0; top: 100%;"
            >
              <li><button class="dropdown-item" type="button" @click="editOffer(offer); openDropdownId = null">Edit</button></li>
              <li><button class="dropdown-item text-danger" type="button" @click="deleteOffer(offer.id); openDropdownId = null">Delete</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    
    <!-- WHAT: Add/Edit Offer Modal Component -->
    <!-- WHY: Separate component for better code organization -->
    <AddOfferModal 
      v-model="showAddOfferModal" 
      :hub-id="hubId" 
      :editing-offer="editingOffer"
      :offer-source="offerSource"
      @offer-added="handleOfferAdded"
      @offer-updated="handleOfferUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import http from '@/lib/http'
import UiBadge from '@/components/ui/UiBadge.vue'
import AddOfferModal from './AddOfferModal.vue'

// WHAT: Component props
// WHY: Receive hub ID and offer source from parent
interface Props {
  hubId: number
  offerSource: 'short_sale' | 'reo'
}

const props = defineProps<Props>()

// WHAT: Offers data and modal state
// WHY: Manage offers display and modal interactions
const offers = ref<any[]>([])
const showAddOfferModal = ref(false)
const openDropdownId = ref<number | null>(null)
const openStatusDropdownId = ref<number | null>(null)
const editingOffer = ref<any>(null)

// WHAT: Load offers for this asset
// WHY: Display current offers from various sources
async function loadOffers() {
  try {
    const response = await http.get(`/am/outcomes/offers/?asset_hub_id=${props.hubId}&offer_source=${props.offerSource}`)
    console.log('Raw offers response:', response.data)
    
    // Handle both paginated and non-paginated responses
    let offersList = []
    if (response.data) {
      if (Array.isArray(response.data)) {
        // Direct array response
        offersList = response.data
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // Paginated response
        offersList = response.data.results
      } else if (typeof response.data === 'object') {
        // Single object response
        offersList = [response.data]
      }
    }
    
    // Filter out any null or invalid offers
    const validOffers = offersList.filter((offer: any) => offer && offer.id)
    offers.value = validOffers
    console.log('Loaded offers:', validOffers)
  } catch (err: any) {
    console.error('Failed to load offers:', err)
    offers.value = []
  }
}

// WHAT: Format currency values for display
// WHY: Show user-friendly currency format
function formatOfferPrice(value: number | string): string {
  if (!value) return '0'
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US').format(numValue)
}

// WHAT: Format offer status for display
// WHY: Show user-friendly status labels
function formatOfferStatus(status: string): string {
  const statusMap: Record<string, string> = {
    'pending': 'Pending',
    'accepted': 'Accepted',
    'rejected': 'Rejected',
    'countered': 'Countered',
    'withdrawn': 'Withdrawn'
  }
  return statusMap[status] || status
}

// WHAT: Get badge tone for offer status
// WHY: Visual indication of offer status
function getOfferStatusTone(status: string): 'success' | 'warning' | 'danger' | 'info' | 'secondary' {
  const toneMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'secondary'> = {
    'pending': 'warning',
    'accepted': 'success',
    'rejected': 'danger',
    'countered': 'info',
    'withdrawn': 'secondary'
  }
  return toneMap[status] || 'secondary'
}

// WHAT: Format financing type for display
// WHY: Show user-friendly financing labels matching modal format
function formatFinancingType(type: string): string {
  const typeMap: Record<string, string> = {
    'cash': 'Cash',
    'conventional': 'Conventional Financing',
    'fha': 'FHA Financing',
    'va': 'VA Financing',
    'usda': 'USDA Financing',
    'hard_money': 'Hard Money',
    'other': 'Other Financing'
  }
  return typeMap[type] || type
}

// WHAT: Format date for display
// WHY: Show user-friendly date format
function formatDate(dateStr: string): string {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleDateString()
  } catch {
    return dateStr
  }
}

// WHAT: Edit an existing offer
// WHY: Allow modification of offer details
function editOffer(offer: any) {
  editingOffer.value = { ...offer }
  showAddOfferModal.value = true
}

// WHAT: Delete an offer
// WHY: Remove unwanted or invalid offers
async function deleteOffer(offerId: number) {
  if (!confirm('Are you sure you want to delete this offer?')) return
  
  try {
    await http.delete(`/am/outcomes/offers/${offerId}/`)
    await loadOffers() // Refresh the list
  } catch (err: any) {
    console.error('Failed to delete offer:', err)
    alert('Failed to delete offer. Please try again.')
  }
}

// WHAT: Handle offer added event from modal
// WHY: Refresh offers list when new offer is created
function handleOfferAdded() {
  editingOffer.value = null
  loadOffers()
}

// WHAT: Handle offer updated event from modal
// WHY: Refresh offers list when offer is updated
function handleOfferUpdated() {
  editingOffer.value = null
  loadOffers()
}

// WHAT: Toggle dropdown menu for offer actions
// WHY: Show/hide edit and delete options
function toggleDropdown(offerId: number) {
  if (openDropdownId.value === offerId) {
    openDropdownId.value = null
  } else {
    openDropdownId.value = offerId
  }
}

// WHAT: Toggle status dropdown for inline editing
// WHY: Allow quick status changes without full edit modal
function toggleStatusDropdown(offerId: number) {
  if (openStatusDropdownId.value === offerId) {
    openStatusDropdownId.value = null
  } else {
    openStatusDropdownId.value = offerId
  }
}

// WHAT: Update offer status inline
// WHY: Quick status changes without opening full edit modal
async function updateOfferStatus(offerId: number, newStatus: string) {
  try {
    await http.patch(`/am/outcomes/offers/${offerId}/`, { offer_status: newStatus })
    openStatusDropdownId.value = null
    await loadOffers() // Refresh to show updated status
  } catch (err: any) {
    console.error('Failed to update offer status:', err)
    alert('Failed to update status. Please try again.')
  }
}

// WHAT: Handle click outside to close dropdowns
// WHY: Improve user experience
function handleDocClick(e: MouseEvent) {
  const target = e.target as Element
  const dropdownButton = target.closest('.dropdown button')
  
  // Close offer action dropdown if clicking outside
  if (openDropdownId.value !== null && !dropdownButton) {
    openDropdownId.value = null
  }
  
  // Close status dropdown if clicking outside
  if (openStatusDropdownId.value !== null && !dropdownButton) {
    openStatusDropdownId.value = null
  }
}

// WHAT: Initialize component
// WHY: Load offers and setup event listeners
onMounted(() => {
  loadOffers()
  document.addEventListener('click', handleDocClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocClick)
})

// WHAT: Expose load function for parent components
// WHY: Allow parent to refresh offers when needed
defineExpose({
  loadOffers
})
</script>

<style scoped>
.offers-list {
  background-color: transparent;
  padding: 0.25rem 0.25rem 0.75rem 0.25rem;
}

.offer-item {
  padding: 0.75rem;
  margin: 0.25rem;
  border-bottom: none;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.offer-item:last-child {
  border-bottom: none;
}

.offer-menu-btn {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  line-height: 1;
  min-width: 1.5rem;
  height: 1.5rem;
  border-color: #6c757d;
}

.offer-menu-btn:hover {
  background-color: #f8f9fa;
  border-color: #495057;
}

.btn-xs {
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  line-height: 1;
  border-radius: 0.25rem;
}
</style>
