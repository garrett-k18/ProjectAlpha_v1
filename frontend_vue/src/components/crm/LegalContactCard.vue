<template>
  <!-- Legal Contact Card with Flip Animation -->
  <!-- WHAT: Card flip feature - front shows title, back shows contact details -->
  <!-- WHY: Cleaner UI with interactive reveal of contact information -->
  <!-- HOW: CSS 3D transforms with Vue reactive state for flip control -->
  <!-- WHAT: Dynamic z-index - increases when dropdown is open -->
  <!-- WHY: Ensure dropdown appears above all other cards in the grid -->
  <!-- HOW: Use computed z-index that increases to 10000 when assignMenuOpen is true -->
  <div class="flip-card" @click="flipCard" :style="{ position: 'relative', zIndex: assignMenuOpen ? 10000 : 1 }">
    <div class="flip-card-inner" :class="{ 'flipped': isFlipped }">
      
      <!-- FRONT SIDE - Title + Firm name -->
      <div class="flip-card-front card border-primary mb-3 bg-secondary-subtle shadow-sm rounded-2">
        <div class="card-body p-2 position-relative">
          <!-- Title in top left corner -->
          <div class="position-absolute top-0 start-0 p-2">
            <div class="small text-muted fw-bold">Legal</div>
          </div>
          <!-- Center content with firm name -->
          <div class="d-flex align-items-center justify-content-center h-100 pt-3">
            <div class="text-center">
              <i class="fas fa-scale-balance text-primary mb-2" style="font-size: 1.5rem;"></i>
              <div class="fw-bold text-dark">
                {{ contact?.firm || label || 'Foreclosure Attorney' }}
              </div>
              <div class="small text-muted">Click to view contact</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- BACK SIDE - Full contact information -->
      <div class="flip-card-back card border-primary mb-3 bg-secondary-subtle shadow-sm rounded-2">
        <div class="card-body p-2">
          <!-- Section title with button -->
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div class="small text-muted fw-bold">Legal</div>
            <div class="position-relative" ref="assignMenuRef">
              <button 
                class="btn btn-sm btn-outline-primary px-2 py-0" 
                style="font-size: 0.65rem;" 
                :title="contact ? 'Re-assign Attorney' : 'Assign Attorney'"
                @click.stop="toggleAssignMenu"
              >
                {{ contact ? 'Re-assign' : 'Assign' }}
              </button>
              <!-- Dropdown menu with legal contacts -->
              <div 
                v-if="assignMenuOpen" 
                class="card shadow-sm mt-1" 
                style="position: absolute; right: 0; min-width: 280px; max-height: 300px; overflow-y: auto; z-index: 9999;"
              >
                <div class="list-group list-group-flush">
                  <!-- Create New button -->
                  <button
                    type="button"
                    class="list-group-item list-group-item-action p-2 small border-bottom bg-primary-subtle"
                    @click="openCreateModal"
                  >
                    <i class="fas fa-plus-circle me-2 text-primary"></i>
                    <span class="fw-bold text-primary">Create New Attorney</span>
                  </button>
                  <!-- Loading state -->
                  <div v-if="loadingAttorneys" class="p-3 text-center text-muted small">
                    <i class="fas fa-spinner fa-spin me-1"></i>
                    Loading attorneys...
                  </div>
                  <!-- Attorney list -->
                  <button
                    v-for="attorney in legalContacts"
                    :key="attorney.id"
                    type="button"
                    class="list-group-item list-group-item-action p-2 small"
                    @click="selectAttorney(attorney.id)"
                  >
                    <div class="fw-bold">{{ attorney.firm }}</div>
                    <div class="text-muted" style="font-size: 0.85em;">{{ attorney.contact_name }}</div>
                  </button>
                  <!-- Empty state -->
                  <div v-if="!loadingAttorneys && legalContacts.length === 0" class="p-3 text-center text-muted small">
                    No attorneys found
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Attorney contact info -->
          <div class="text-center">
            <div class="d-flex flex-column gap-1">
              <!-- Firm name -->
              <div class="small fw-bold text-dark">
                {{ contact?.firm || label || 'Foreclosure Attorney' }}
              </div>
              <!-- Contact details: email and phone on single line -->
              <div class="d-flex justify-content-center gap-3 flex-wrap">
                <a 
                  v-if="contact?.email" 
                  :href="`mailto:${contact.email}`" 
                  class="small text-primary text-decoration-none"
                >
                  {{ contact.email }}
                </a>
                <a 
                  v-if="contact?.phone" 
                  :href="`tel:${contact.phone}`" 
                  class="small text-primary text-decoration-none"
                >
                  {{ contact.phone }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
  </div>
  
  <!-- Create CRM Contact Modal -->
  <CreateCrmContactModal 
    :show="showCreateModal" 
    contact-type="legal"
    @close="showCreateModal = false"
    @created="handleContactCreated"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import type { CrmContact } from '@/stores/outcomes'
import http from '@/lib/http'
import CreateCrmContactModal from './CreateCrmContactModal.vue'

// Props: contact details and optional custom label
const props = defineProps<{
  contact: CrmContact | null
  label?: string
}>()

// Emits: when attorney is selected or view CRM is clicked
const emit = defineEmits<{
  (e: 'assign', crmId: number): void
  (e: 'view-crm', crmId: number): void
}>()

// Card flip state
const isFlipped = ref(false)

// Dropdown state for attorney assignment
const assignMenuOpen = ref(false)
const assignMenuRef = ref<HTMLElement | null>(null)
const legalContacts = ref<CrmContact[]>([])
const loadingAttorneys = ref(false)

// WHAT: Create modal state
// WHY: Control visibility of CreateCrmContactModal
// HOW: Boolean ref toggled by openCreateModal function
const showCreateModal = ref(false)

/**
 * Toggle card flip animation
 * WHAT: Flips between front (title) and back (contact details)
 * WHY: Provides clean, interactive way to reveal contact information
 * HOW: Toggles CSS class that triggers 3D transform animation
 */
function flipCard() {
  isFlipped.value = !isFlipped.value
}

/**
 * Toggle the assignment dropdown menu
 * Fetches legal contacts on first open
 */
async function toggleAssignMenu() {
  assignMenuOpen.value = !assignMenuOpen.value
  if (assignMenuOpen.value && legalContacts.value.length === 0) {
    await fetchLegalContacts()
  }
}

/**
 * Fetch all legal contacts from CRM
 * Uses the /core/crm/legal/ endpoint which filters by tag='legal'
 */
async function fetchLegalContacts() {
  try {
    loadingAttorneys.value = true
    const res = await http.get<{ results: CrmContact[] } | CrmContact[]>('/core/crm/legal/')
    // DRF returns paginated response: {count, next, previous, results}
    // Extract results array from paginated response
    legalContacts.value = Array.isArray(res.data) 
      ? res.data 
      : (res.data as any).results || []
  } catch (err: any) {
    console.error('Failed to fetch legal contacts:', err)
    legalContacts.value = []
  } finally {
    loadingAttorneys.value = false
  }
}

/**
 * Handle attorney selection from dropdown
 * Emits the selected CRM ID to parent component
 */
function selectAttorney(crmId: number) {
  emit('assign', crmId)
  assignMenuOpen.value = false
}

/**
 * WHAT: Open create modal for new attorney
 * WHY: Allow users to create attorneys without leaving this screen
 * HOW: Close dropdown, open CreateCrmContactModal
 */
function openCreateModal() {
  assignMenuOpen.value = false
  showCreateModal.value = true
}

/**
 * WHAT: Handle newly created contact
 * WHY: Auto-select and assign newly created attorney
 * HOW: Reload contacts list, then auto-select the new contact
 */
async function handleContactCreated(crmId: number) {
  console.log('New attorney created with ID:', crmId)
  // WHAT: Reload legal contacts to include the new attorney
  // WHY: New attorney needs to appear in dropdown for future selections
  await fetchLegalContacts()
  // WHAT: Auto-assign the newly created attorney
  // WHY: User probably wants to assign the contact they just created
  emit('assign', crmId)
}

/**
 * Close dropdown when clicking outside
 * Listens for document clicks and checks if click is outside the dropdown
 */
function handleDocClick(e: MouseEvent) {
  const assignRoot = assignMenuRef.value
  if (assignRoot && assignMenuOpen.value && !assignRoot.contains(e.target as Node)) {
    assignMenuOpen.value = false
  }
}

// Lifecycle: Add/remove click listener for closing dropdown
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))
</script>

<style scoped>
/* ============================================================================ */
/* CARD FLIP ANIMATION - 3D CSS Transform Effect */
/* ============================================================================ */

.flip-card {
  background-color: transparent;
  perspective: 1000px; /* 3D perspective for flip effect */
  cursor: pointer;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100px; /* Fixed height to prevent overlap */
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card-inner.flipped {
  transform: rotateY(180deg);
}

.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 100px; /* Fixed height for consistent flip animation */
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

.flip-card-front {
  /* Front side is visible by default - no additional styles needed */
  z-index: 2;
}

.flip-card-back {
  /* Back side is rotated 180 degrees initially (hidden) */
  transform: rotateY(180deg);
}

/* Hover effect for better UX */
.flip-card:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}
</style>
