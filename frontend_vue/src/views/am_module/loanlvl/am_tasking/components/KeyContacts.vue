<!--
  WHAT: Key Contacts widget - CLEAN REBUILD
  WHY: Display primary contacts for the asset
  WHERE: AM Tasking tab, activity widgets row
  HOW: Fetches contact data and displays in grid layout
-->
<template>
  <div class="contacts-card">
    <!-- Header -->
    <div class="contacts-card-header">
      <h4 class="contacts-card-title">Key Contacts</h4>
      <i class="mdi mdi-account-multiple text-muted"></i>
    </div>

    <!-- Body -->
    <div class="contacts-card-body">
      <div class="contacts-grid">
        <!-- Legal Contact -->
        <div class="contact-col">
          <LegalContactCard 
            :contact="legalContact" 
            label="Foreclosure Attorney"
            @assign="handleAssignLegal"
          />
        </div>
        
        <!-- Servicer Contact -->
        <div class="contact-col">
          <ServicerContactCard 
            :contact="servicerContact" 
            label="Loan Servicer"
            @assign="handleAssignServicer"
          />
        </div>
        
        <!-- Agent Contact -->
        <div class="contact-col">
          <AgentContactCard 
            :contact="agentContact" 
            label="Real Estate Agent"
            @assign="handleAssignAgent"
          />
        </div>
        
        <!-- Contractor Contact -->
        <div class="contact-col">
          <ContractorContactCard 
            :contact="contractorContact" 
            label="Contractor"
            @assign="handleAssignContractor"
          />
        </div>
        
        <!-- Title Company Contact -->
        <div class="contact-col">
          <TitleCompanyContactCard 
            :contact="titleCompanyContact" 
            label="Title Company"
            @assign="handleAssignTitleCompany"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '@/lib/http'
import LegalContactCard from '@/components/crm/LegalContactCard.vue'
import ServicerContactCard from '@/components/crm/ServicerContactCard.vue'
import AgentContactCard from '@/components/crm/AgentContactCard.vue'
import ContractorContactCard from '@/components/crm/ContractorContactCard.vue'
import TitleCompanyContactCard from '@/components/crm/TitleCompanyContactCard.vue'

const props = defineProps<{
  hubId: number
}>()

// WHAT: Contact data refs
const legalContact = ref<any>(null)
const servicerContact = ref<any>(null)
const agentContact = ref<any>(null)
const contractorContact = ref<any>(null)
const titleCompanyContact = ref<any>(null)

// WHAT: Load all contacts for this asset
async function loadContacts() {
  try {
    const response = await http.get(`/am/contacts/`, {
      params: { asset_hub_id: props.hubId }
    })
    
    if (response.data) {
      legalContact.value = response.data.legal || null
      servicerContact.value = response.data.servicer || null
      agentContact.value = response.data.agent || null
      contractorContact.value = response.data.contractor || null
      titleCompanyContact.value = response.data.title_company || null
    }
  } catch (err) {
    console.error('Failed to load contacts:', err)
  }
}

// WHAT: Assignment handlers
async function handleAssignLegal(contactId: number) {
  try {
    await http.post(`/am/contacts/assign/`, {
      asset_hub_id: props.hubId,
      contact_type: 'legal',
      contact_id: contactId
    })
    await loadContacts()
  } catch (err) {
    console.error('Failed to assign legal contact:', err)
  }
}

async function handleAssignServicer(contactId: number) {
  try {
    await http.post(`/am/contacts/assign/`, {
      asset_hub_id: props.hubId,
      contact_type: 'servicer',
      contact_id: contactId
    })
    await loadContacts()
  } catch (err) {
    console.error('Failed to assign servicer contact:', err)
  }
}

async function handleAssignAgent(contactId: number) {
  try {
    await http.post(`/am/contacts/assign/`, {
      asset_hub_id: props.hubId,
      contact_type: 'agent',
      contact_id: contactId
    })
    await loadContacts()
  } catch (err) {
    console.error('Failed to assign agent contact:', err)
  }
}

async function handleAssignContractor(contactId: number) {
  try {
    await http.post(`/am/contacts/assign/`, {
      asset_hub_id: props.hubId,
      contact_type: 'contractor',
      contact_id: contactId
    })
    await loadContacts()
  } catch (err) {
    console.error('Failed to assign contractor contact:', err)
  }
}

async function handleAssignTitleCompany(contactId: number) {
  try {
    await http.post(`/am/contacts/assign/`, {
      asset_hub_id: props.hubId,
      contact_type: 'title_company',
      contact_id: contactId
    })
    await loadContacts()
  } catch (err) {
    console.error('Failed to assign title company contact:', err)
  }
}

onMounted(() => {
  loadContacts()
})
</script>

<style scoped>
/* WHAT: Card container */
.contacts-card {
  background: #FDFBF7;
  border-radius: 0.375rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* WHAT: Card header */
.contacts-card-header {
  background: transparent;
  border-bottom: 1px solid #dee2e6;
  padding: 1rem;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.contacts-card-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  color: #212529;
}

/* WHAT: Card body */
.contacts-card-body {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

/* WHAT: Contacts grid - 2 columns */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.contact-col {
  min-width: 0;
}
</style>
