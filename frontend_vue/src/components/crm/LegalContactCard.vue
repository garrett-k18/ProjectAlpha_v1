<template>
  <!-- Foreclosure Attorney Contact Card -->
  <!-- Component displays assigned legal contact with firm name and assign dropdown -->
  <!-- Used in: FcCard.vue and other outcome cards requiring legal contact assignment -->
  <div class="card border-primary mb-3 bg-secondary-subtle shadow-sm rounded-2">
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
            style="position: absolute; right: 0; min-width: 280px; max-height: 300px; overflow-y: auto; z-index: 1060;"
          >
            <div class="list-group list-group-flush">
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
          <!-- Contact details: email and phone with clickable links (only when assigned) -->
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
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import type { CrmContact } from '@/stores/outcomes'
import http from '@/lib/http'

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

// Dropdown state for attorney assignment
const assignMenuOpen = ref(false)
const assignMenuRef = ref<HTMLElement | null>(null)
const legalContacts = ref<CrmContact[]>([])
const loadingAttorneys = ref(false)

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
