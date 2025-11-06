<template>
  <!-- Title Company Contact Card with Flip Animation -->
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
        <div class="card-body p-1 position-relative">
          <!-- Title in top left corner -->
          <div class="position-absolute top-0 start-0 p-1">
            <div class="small text-muted fw-bold">Title Company</div>
          </div>
          <!-- Center content with firm name -->
          <div class="d-flex align-items-center justify-content-center h-100 pt-2">
            <div class="text-center">
              <i class="fas fa-file-contract text-primary mb-1" style="font-size: 1.2rem;"></i>
              <div class="fw-bold text-dark small">
                {{ contact?.firm || label || 'Title Company' }}
              </div>
              <div class="small text-muted" style="font-size: 0.7rem;">Click to view</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- BACK SIDE - Full contact information -->
      <div class="flip-card-back card border-primary mb-3 bg-secondary-subtle shadow-sm rounded-2">
        <div class="card-body p-1">
          <!-- Section title with button -->
          <div class="d-flex justify-content-between align-items-center mb-1">
            <div class="small text-muted fw-bold">Title Company</div>
            <div class="position-relative" ref="assignMenuRef">
              <button 
                class="btn btn-sm btn-outline-primary px-1 py-0" 
                style="font-size: 0.6rem;" 
                :title="contact ? 'Re-assign Title Company' : 'Assign Title Company'"
                @click.stop="toggleAssignMenu"
              >
                {{ contact ? 'Re-assign' : 'Assign' }}
              </button>
              <!-- Dropdown menu with title company contacts -->
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
                    <span class="fw-bold text-primary">Create New Title Company</span>
                  </button>
                  <!-- Loading state -->
                  <div v-if="loadingTitleCompanies" class="p-3 text-center text-muted small">
                    <i class="fas fa-spinner fa-spin me-1"></i>
                    Loading title companies...
                  </div>
                  <!-- Title Company list -->
                  <button
                    v-for="titleCompany in titleCompanyContacts"
                    :key="titleCompany.id"
                    type="button"
                    class="list-group-item list-group-item-action p-2 small"
                    @click="selectTitleCompany(titleCompany.id)"
                  >
                    <div class="fw-bold">{{ titleCompany.firm }}</div>
                    <div class="text-muted" style="font-size: 0.85em;">{{ titleCompany.contact_name }}</div>
                  </button>
                  <!-- Empty state -->
                  <div v-if="!loadingTitleCompanies && titleCompanyContacts.length === 0" class="p-3 text-center text-muted small">
                    No title companies found
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- Title Company contact info -->
          <div class="text-center">
            <div class="d-flex flex-column" style="gap: 0.25rem;">
              <!-- Firm name -->
              <div class="small fw-bold text-dark" style="font-size: 0.8rem;">
                {{ contact?.firm || label || 'Title Company' }}
              </div>
              <!-- Contact details: email and phone on single line -->
              <div class="d-flex justify-content-center gap-2 flex-wrap">
                <a 
                  v-if="contact?.email" 
                  :href="`mailto:${contact.email}`" 
                  class="text-primary text-decoration-none"
                  style="font-size: 0.7rem;"
                >
                  {{ contact.email }}
                </a>
                <a 
                  v-if="contact?.phone" 
                  :href="`tel:${contact.phone}`" 
                  class="text-primary text-decoration-none"
                  style="font-size: 0.7rem;"
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
    contact-type="title_company"
    @close="showCreateModal = false"
    @created="handleContactCreated"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import type { CrmContact } from '@/stores/outcomes'
import http from '@/lib/http'
import CreateCrmContactModal from './CreateCrmContactModal.vue'

// WHAT: Props for contact details and optional custom label
// WHY: Allow parent component to pass in contact data and customize label
// HOW: Define props with TypeScript types for type safety
const props = defineProps<{
  contact: CrmContact | null
  label?: string
}>()

// WHAT: Emits for assignment and view CRM events
// WHY: Notify parent component when title company is selected
// HOW: Define typed emits with event name and payload type
const emit = defineEmits<{
  (e: 'assign', crmId: number): void
  (e: 'view-crm', crmId: number): void
}>()

// WHAT: Card flip state
// WHY: Track whether card is showing front or back
// HOW: Boolean ref toggled by flipCard function
const isFlipped = ref(false)

// WHAT: Dropdown state for title company assignment
// WHY: Control visibility and data for assignment dropdown menu
// HOW: Reactive refs for menu state, contacts list, and loading state
const assignMenuOpen = ref(false)
const assignMenuRef = ref<HTMLElement | null>(null)
const titleCompanyContacts = ref<CrmContact[]>([])
const loadingTitleCompanies = ref(false)

// WHAT: Create modal state
// WHY: Control visibility of CreateCrmContactModal
// HOW: Boolean ref toggled by openCreateModal function
const showCreateModal = ref(false)

/**
 * WHAT: Toggle card flip animation
 * WHY: Provides clean, interactive way to reveal contact information
 * HOW: Toggles CSS class that triggers 3D transform animation
 */
function flipCard() {
  isFlipped.value = !isFlipped.value
}

/**
 * WHAT: Toggle the assignment dropdown menu
 * WHY: Show/hide dropdown for selecting title company
 * HOW: Fetches title company contacts on first open
 */
async function toggleAssignMenu() {
  assignMenuOpen.value = !assignMenuOpen.value
  if (assignMenuOpen.value && titleCompanyContacts.value.length === 0) {
    await fetchTitleCompanyContacts()
  }
}

/**
 * WHAT: Fetch all title company contacts from CRM
 * WHY: Populate dropdown with available title companies for assignment
 * HOW: Uses the /core/crm/ endpoint filtered by tag='title_company'
 */
async function fetchTitleCompanyContacts() {
  try {
    loadingTitleCompanies.value = true
    // WHAT: Query MasterCRM for title_company tag
    // WHY: Get all title companies for assignment dropdown
    // WHERE: /api/core/crm/?tag=title_company endpoint
    const res = await http.get<{ results: CrmContact[] } | CrmContact[]>('/core/crm/', {
      params: { tag: 'title_company' }
    })
    // WHAT: Extract results array from paginated response
    // WHY: DRF returns paginated response: {count, next, previous, results}
    // HOW: Check if response is array or object with results property
    titleCompanyContacts.value = Array.isArray(res.data) 
      ? res.data 
      : (res.data as any).results || []
  } catch (err: any) {
    console.error('Failed to fetch title company contacts:', err)
    titleCompanyContacts.value = []
  } finally {
    loadingTitleCompanies.value = false
  }
}

/**
 * WHAT: Handle title company selection from dropdown
 * WHY: Emit selected CRM ID to parent for assignment
 * HOW: Emits 'assign' event with CRM ID and closes dropdown
 */
function selectTitleCompany(crmId: number) {
  emit('assign', crmId)
  assignMenuOpen.value = false
}

/**
 * WHAT: Open create modal for new title company
 * WHY: Allow users to create title companies without leaving this screen
 * HOW: Close dropdown, open CreateCrmContactModal
 */
function openCreateModal() {
  assignMenuOpen.value = false
  showCreateModal.value = true
}

/**
 * WHAT: Handle newly created contact
 * WHY: Auto-select and assign newly created title company
 * HOW: Reload contacts list, then auto-select the new contact
 */
async function handleContactCreated(crmId: number) {
  console.log('New title company created with ID:', crmId)
  // WHAT: Reload title company contacts to include the new entry
  // WHY: New title company needs to appear in dropdown for future selections
  await fetchTitleCompanyContacts()
  // WHAT: Auto-assign the newly created title company
  // WHY: User probably wants to assign the contact they just created
  emit('assign', crmId)
}

/**
 * WHAT: Close dropdown when clicking outside
 * WHY: Standard UX pattern for dropdown menus
 * HOW: Listens for document clicks and checks if click is outside the dropdown
 */
function handleDocClick(e: MouseEvent) {
  const assignRoot = assignMenuRef.value
  if (assignRoot && assignMenuOpen.value && !assignRoot.contains(e.target as Node)) {
    assignMenuOpen.value = false
  }
}

// WHAT: Lifecycle hooks for click listener
// WHY: Add listener on mount, remove on unmount to prevent memory leaks
// HOW: Use onMounted and onBeforeUnmount Vue composition API hooks
onMounted(() => document.addEventListener('click', handleDocClick))
onBeforeUnmount(() => document.removeEventListener('click', handleDocClick))
</script>

<style scoped>
/* ============================================================================ */
/* CARD FLIP ANIMATION - 3D CSS Transform Effect */
/* ============================================================================ */

/* WHAT: Container for flip card with 3D perspective */
/* WHY: Enable 3D transformation effect for card flip */
/* HOW: Set perspective for 3D space and cursor to indicate interactivity */
.flip-card {
  background-color: transparent;
  perspective: 1000px; /* 3D perspective for flip effect */
  cursor: pointer;
}

/* WHAT: Inner container that performs the flip transformation */
/* WHY: Preserve 3D transformations for child elements (front/back sides) */
/* HOW: Use transform-style: preserve-3d and transition for smooth animation */
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 75px; /* Reduced height for more compact cards */
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

/* WHAT: Flipped state class that rotates card 180 degrees */
/* WHY: Show back side when card is clicked */
/* HOW: Apply rotateY(180deg) transform when flipped class is present */
.flip-card-inner.flipped {
  transform: rotateY(180deg);
}

/* WHAT: Front and back sides of the card */
/* WHY: Position both sides in same space with backface hidden for flip effect */
/* HOW: Absolute positioning with backface-visibility: hidden */
.flip-card-front, .flip-card-back {
  position: absolute;
  width: 100%;
  height: 75px; /* Reduced height for more compact cards */
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

/* WHAT: Front side of card (visible by default) */
/* WHY: Show front side initially before flip */
/* HOW: Higher z-index to ensure it's on top */
.flip-card-front {
  /* Front side is visible by default - no additional styles needed */
  z-index: 2;
}

/* WHAT: Back side of card (rotated 180 degrees initially) */
/* WHY: Hidden until card is flipped */
/* HOW: Pre-rotate 180 degrees so it aligns correctly when parent rotates */
.flip-card-back {
  /* Back side is rotated 180 degrees initially (hidden) */
  transform: rotateY(180deg);
}

/* WHAT: Hover effect for better UX */
/* WHY: Visual feedback when hovering over card */
/* HOW: Slight scale increase on hover */
.flip-card:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}
</style>

