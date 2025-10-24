<template>
  <!--
    WHAT: Key Contacts card displaying Foreclosure Attorney and Servicer
    WHY: Quick access to primary contacts for the loan
    WHERE: AM Tasking page, after Upcoming Deadlines
    HOW: Displays LegalContactCard and ServicerContactCard components
  -->
  <div class="card h-100">
    <div class="card-header d-flex align-items-center justify-content-between">
      <h4 class="header-title mb-0">Key Contacts</h4>
      <i class="mdi mdi-account-multiple text-muted"></i>
    </div>
    <div class="card-body py-2">
      <div class="row g-2">
        <!-- Legal Contact Column -->
        <div class="col-md-6">
          <LegalContactCard 
            :contact="legalContact" 
            label="Foreclosure Attorney"
            @assign="handleAssignLegal"
          />
        </div>
        
        <!-- Servicer Contact Column -->
        <div class="col-md-6">
          <ServicerContactCard 
            :contact="servicerContact" 
            label="Loan Servicer"
            @assign="handleAssignServicer"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '@/lib/http'
// Reusable legal contact card with assignment dropdown
// Path: src/components/crm/LegalContactCard.vue
import LegalContactCard from '@/components/crm/LegalContactCard.vue'
// Reusable servicer contact card with assignment dropdown
// Path: src/components/crm/ServicerContactCard.vue
import ServicerContactCard from '@/components/crm/ServicerContactCard.vue'

const props = defineProps<{
  hubId: number
}>()

// Contact data from AssetCRMContact
const legalContact = ref<any>(null)
const servicerContact = ref<any>(null)

/**
 * Load key contacts for this asset hub
 * Fetches legal and servicer contacts from AssetCRMContact
 */
async function loadContacts() {
  try {
    // WHAT: Load legal contact from AssetCRMContact
    // WHY: Legal contacts are now stored in junction table, not FC outcome
    // WHERE: /api/am/asset-crm-contacts/?asset_hub=X&role=legal
    const legalRes = await http.get(`/am/asset-crm-contacts/`, {
      params: { asset_hub: props.hubId, role: 'legal' }
    })
    
    // Get first legal contact if exists
    const legals = Array.isArray(legalRes.data) ? legalRes.data : legalRes.data.results || []
    if (legals.length > 0) {
      legalContact.value = legals[0].crm_details
    } else {
      legalContact.value = null
    }
    
    // Load servicer contact from AssetCRMContact
    const servicerRes = await http.get(`/am/asset-crm-contacts/`, {
      params: { asset_hub: props.hubId, role: 'servicer' }
    })
    
    // Get first servicer contact if exists
    const servicers = Array.isArray(servicerRes.data) ? servicerRes.data : servicerRes.data.results || []
    if (servicers.length > 0) {
      servicerContact.value = servicers[0].crm_details
    } else {
      servicerContact.value = null
    }
  } catch (err: any) {
    console.error('Failed to load key contacts:', err)
  }
}

/**
 * Handle legal contact assignment
 * Creates AssetCRMContact link with role='legal'
 */
async function handleAssignLegal(crmId: number) {
  try {
    console.log('Assigning legal contact:', { asset_hub_id: props.hubId, crm_id: crmId, role: 'legal' })
    
    // WHAT: Create or update AssetCRMContact with role='legal'
    // WHY: Store legal contact assignment in junction table
    // WHERE: POST /api/am/asset-crm-contacts/
    const response = await http.post(`/am/asset-crm-contacts/`, {
      asset_hub_id: props.hubId,
      crm_id: crmId,
      role: 'legal'
    })
    
    console.log('Assignment successful:', response.data)
    
    // WHAT: Reload contacts to show updated attorney
    // WHY: Display newly assigned legal contact
    await loadContacts()
  } catch (err: any) {
    console.error('Failed to assign attorney:', err)
    console.error('Error response:', err.response?.data)
    console.error('Error status:', err.response?.status)
    alert(`Failed to assign attorney: ${err.response?.data?.detail || err.message}`)
  }
}

/**
 * Handle servicer contact assignment
 * Creates AssetCRMContact link with role='servicer'
 */
async function handleAssignServicer(crmId: number) {
  try {
    console.log('Assigning servicer contact:', { asset_hub_id: props.hubId, crm_id: crmId, role: 'servicer' })
    
    // Create or update AssetCRMContact with role='servicer'
    const response = await http.post(`/am/asset-crm-contacts/`, {
      asset_hub_id: props.hubId,
      crm_id: crmId,
      role: 'servicer'
    })
    
    console.log('Servicer assignment successful:', response.data)
    
    // Reload contacts to show updated servicer
    await loadContacts()
  } catch (err: any) {
    console.error('Failed to assign servicer:', err)
    console.error('Error response:', err.response?.data)
    console.error('Error status:', err.response?.status)
    alert(`Failed to assign servicer: ${err.response?.data?.detail || err.message}`)
  }
}

onMounted(() => {
  loadContacts()
})
</script>
