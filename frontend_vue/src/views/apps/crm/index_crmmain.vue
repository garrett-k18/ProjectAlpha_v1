<template>
  <!--
    CRM Hub Page
    Location: frontend_vue/src/views/apps/crm/index_crmmain.vue
    Purpose: Single consolidated CRM view with secondary sidebar to switch between
    Broker, Trading Partner, Investor, Legal, and Management CRM lists.
    Uses the master CRMListView component with configuration-driven approach.
  -->
  <Layout>
    <!-- Primary breadcrumb for the CRM hub -->
    <Breadcrumb :title="title" :items="breadcrumbItems" />

    <b-row>
      <!-- Sidebar with CRM type selector -->
      <b-col xl="3" lg="4" class="mb-3 mb-xl-0">
        <div class="card h-100">
          <div class="card-header">
            <h5 class="card-title mb-0">CRM Lists</h5>
          </div>
          <div class="card-body p-0">
            <div class="crm-list">
              <div
                v-for="crmType in crmTypes"
                :key="crmType.key"
                class="crm-list-item"
                :class="{ 'crm-list-item-selected': crmType.key === activeCrmType }"
                role="button"
                @click="activeCrmType = crmType.key"
              >
                <span class="crm-item-icon">
                  <i :class="crmType.icon"></i>
                </span>
                <div class="crm-item-content">
                  <div class="crm-item-title">{{ crmType.label }}</div>
                  <small class="crm-item-caption">{{ crmType.caption }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </b-col>

      <!-- Main content: single CRMListView with dynamic configuration -->
      <b-col xl="9" lg="8">
        <div class="mb-3">
          <h4 class="mb-0">{{ activeConfig.entityType }}s</h4>
          <small class="text-muted">{{ activeCrmTypeCaption }}</small>
        </div>
        <CRMListView
          :key="activeCrmType"
          :entity-type="activeConfig.entityType"
          :columns="activeConfig.columns"
          :filters="activeConfig.filters"
          :data="activeStore.results"
          :loading="activeStore.loading"
          :error="activeStore.error"
          :add-button-text="activeConfig.addButtonText"
          @search="onSearch"
          @filter="onFilter"
          @create="onCreate"
          @update="onUpdate"
          @export="onExport"
          @view-nda="onViewNDA"
        />
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
import CRMListView from '@/views/apps/crm/components/index_mastercrm.vue'
import { useBrokersCrmStore } from '@/stores/brokerscrm'
import { useTradingPartnersStore } from '@/stores/tradingPartners'
import http from '@/lib/http'

// Define CRM types available in the secondary sidebar
const CRM_TYPES = [
  {
    key: 'brokers',
    label: 'Brokers',
    caption: 'Manage broker contacts and coverage states.',
    icon: 'mdi mdi-account-tie',
  },
  {
    key: 'tradingpartners',
    label: 'Trading Partners',
    caption: 'Track trading partners and NDA status.',
    icon: 'mdi mdi-swap-horizontal',
  },
  {
    key: 'investors',
    label: 'Investors',
    caption: 'Investor relationships and preferences.',
    icon: 'mdi mdi-account-cash',
  },
  {
    key: 'legal',
    label: 'Legal',
    caption: 'Legal contacts and documents.',
    icon: 'mdi mdi-scale-balance',
  },
  {
    key: 'management',
    label: 'Management',
    caption: 'Internal management stakeholders.',
    icon: 'mdi mdi-account-group',
  },
]

export default defineComponent({
  name: 'CRMMainIndex',
  components: {
    Layout,
    Breadcrumb,
    CRMListView,
  },
  setup() {
    // Track the currently selected CRM type
    const activeCrmType = ref('brokers')
    const statesOptions = ref<Array<{ value: string; label: string }>>([])

    // Initialize stores
    const brokersStore = useBrokersCrmStore()
    const tradingPartnersStore = useTradingPartnersStore()

    // Compute the active store based on selected CRM type
    const activeStore = computed(() => {
      switch (activeCrmType.value) {
        case 'brokers':
          return brokersStore
        case 'tradingpartners':
          return tradingPartnersStore
        // Add other stores as needed
        default:
          return { results: [], loading: false, error: null }
      }
    })

    // Compute the active configuration (columns, filters, etc.) based on type
    const activeConfig = computed(() => {
      const formatPhone = (phone: string | null): string => {
        const digits = (phone || '').replace(/\D/g, '')
        if (digits.length === 10) {
          return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`
        }
        return phone || '—'
      }

      const formatDate = (dateStr: string | null): string => {
        if (!dateStr) return ''
        try {
          return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          })
        } catch {
          return dateStr
        }
      }

      switch (activeCrmType.value) {
        case 'brokers':
          return {
            entityType: 'Broker',
            addButtonText: 'Add Broker',
            columns: [
              { field: 'firm', header: 'Brokerage', editable: true, placeholder: 'ABC Realty' },
              {
                field: 'name',
                header: 'Broker Name',
                editable: true,
                placeholder: 'Jane Doe',
                component: 'router-link',
                componentProps: (row: any) => ({
                  to: `/acq/brokers/${row.id}`,
                  class: 'text-body',
                }),
              },
              {
                field: 'locale',
                header: 'MSA',
                formatter: (row: any) => {
                  const city = row.city || ''
                  const state = Array.isArray(row.states) && row.states.length ? row.states[0] : ''
                  if (city && state) return `${city}, ${state}`
                  return city || state || '—'
                },
              },
              {
                field: 'states',
                header: 'States',
                editable: true,
                cols: 6,
                md: 6,
                options: statesOptions.value,
                multiple: true,
              },
              {
                field: 'email',
                header: 'Email',
                editable: true,
                inputType: 'email',
                placeholder: 'jane@example.com',
                formatter: (row: any) => row.email || '—',
                component: 'a',
                componentProps: (row: any) => ({
                  href: `mailto:${row.email}`,
                  class: 'text-primary text-decoration-underline',
                }),
              },
              {
                field: 'phone',
                header: 'Phone',
                editable: true,
                inputType: 'tel',
                placeholder: '(555) 123-4567',
                formatter: (row: any) => formatPhone(row.phone),
                component: 'a',
                componentProps: (row: any) => ({
                  href: `tel:${row.phone}`,
                  class: 'text-primary text-decoration-underline',
                }),
              },
            ],
            filters: [
              {
                field: 'state',
                label: 'State',
                options: Array.from(
                  new Set(
                    brokersStore.results
                      .flatMap((b: any) => (Array.isArray(b.states) ? b.states : []))
                  )
                ).sort(),
              },
            ],
          }

        case 'tradingpartners':
          return {
            entityType: 'Trading Partner',
            addButtonText: 'Add Trading Partner',
            columns: [
              {
                field: 'firm',
                header: 'Firm',
                editable: true,
                placeholder: 'ABC Capital Partners',
                component: 'router-link',
                componentProps: (row: any) => ({
                  to: `/acq/trading-partners/${row.id}`,
                  class: 'text-body',
                }),
              },
              {
                field: 'name',
                header: 'Primary Contact',
                editable: true,
                placeholder: 'John Smith',
              },
              {
                field: 'states',
                header: 'States',
                editable: true,
                cols: 6,
                md: 6,
                options: statesOptions.value,
                multiple: true,
              },
              {
                field: 'email',
                header: 'Email',
                editable: true,
                inputType: 'email',
                placeholder: 'john@example.com',
                component: 'a',
                componentProps: (row: any) => ({
                  href: `mailto:${row.email}`,
                  class: 'text-primary text-decoration-underline',
                }),
              },
              {
                field: 'phone',
                header: 'Phone',
                editable: true,
                inputType: 'tel',
                placeholder: '(555) 123-4567',
                formatter: (row: any) => formatPhone(row.phone),
                component: 'a',
                componentProps: (row: any) => ({
                  href: `tel:${row.phone}`,
                  class: 'text-primary text-decoration-underline',
                }),
              },
              {
                field: 'nda_flag',
                header: 'NDA Signed',
                component: 'div',
                componentProps: (row: any) => ({ class: 'form-check' }),
                formatter: (row: any) => '',
                customRender: true,
              },
              {
                field: 'nda_signed',
                header: 'Date Signed',
                formatter: (row: any) => (row.nda_signed ? formatDate(row.nda_signed) : '—'),
              },
            ],
            filters: [
              { field: 'nda', label: 'NDA Status', options: ['Signed', 'Not Signed'] },
            ],
          }

        // Placeholder configs for other types
        case 'investors':
        case 'legal':
        case 'management':
          return {
            entityType: activeCrmType.value.charAt(0).toUpperCase() + activeCrmType.value.slice(1),
            addButtonText: `Add ${activeCrmType.value.charAt(0).toUpperCase() + activeCrmType.value.slice(1)}`,
            columns: [
              { field: 'name', header: 'Name', editable: true },
              { field: 'email', header: 'Email', editable: true, inputType: 'email' },
              { field: 'phone', header: 'Phone', editable: true, inputType: 'tel' },
            ],
            filters: [],
          }

        default:
          return {
            entityType: 'Contact',
            addButtonText: 'Add Contact',
            columns: [],
            filters: [],
          }
      }
    })

    // Load states for multi-select
    http
      .get('/core/state-assumptions/all/')
      .then((resp) => {
        const results = resp.data?.results || resp.data || []
        statesOptions.value = (results || [])
          .map((s: any) => ({
            value: s.code || s.state_code,
            label: s.name || s.state_name,
          }))
          .sort((a: any, b: any) => a.label.localeCompare(b.label))
      })
      .catch(() => {
        statesOptions.value = []
      })

    // Fetch data when CRM type changes
    const loadData = () => {
      if (activeCrmType.value === 'brokers') {
        brokersStore.fetchBrokers({ page: 1 })
      } else if (activeCrmType.value === 'tradingpartners') {
        tradingPartnersStore.fetchPartners({ page: 1 })
      }
      // Add other types as needed
    }

    // Initial load
    loadData()

    const onSearch = (query: string) => {
      console.log('Search:', query)
      // Implement search
    }

    const onFilter = (filters: Record<string, string>) => {
      console.log('Filter:', filters)
      loadData()
    }

    const onCreate = async (data: any) => {
      if (activeCrmType.value === 'brokers') {
        await brokersStore.createBroker({ ...data, tag: 'broker' })
      } else if (activeCrmType.value === 'tradingpartners') {
        await tradingPartnersStore.createPartner({ ...data, tag: 'trading_partner' })
      }
    }

    const onUpdate = async (payload: { id: number; data: any }) => {
      if (activeCrmType.value === 'brokers') {
        await brokersStore.updateBroker(payload.id, payload.data)
      } else if (activeCrmType.value === 'tradingpartners') {
        await tradingPartnersStore.updatePartner(payload.id, payload.data)
      }
    }

    const onExport = () => {
      console.log('Export', activeCrmType.value)
    }

    const onViewNDA = (partner: any) => {
      if (!partner.nda_flag) {
        alert('No NDA on file for this trading partner.')
        return
      }
      console.log('View NDA for partner:', partner.id)
    }

    // Compute caption for active CRM type
    const activeCrmTypeCaption = computed(() => {
      const currentType = CRM_TYPES.find(t => t.key === activeCrmType.value)
      return currentType ? currentType.caption : ''
    })

    return {
      breadcrumbItems: [
        { text: 'Hyper', href: '/' },
        { text: 'Apps', href: '/apps/calendar' },
        { text: 'CRMs', active: true },
      ],
      crmTypes: CRM_TYPES,
      title: 'CRMs',
      activeCrmType,
      activeStore,
      activeConfig,
      activeCrmTypeCaption,
      onSearch,
      onFilter,
      onCreate,
      onUpdate,
      onExport,
      onViewNDA,
    }
  },
})
</script>

<style scoped>
.crm-list-item {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
  cursor: pointer;
}

.crm-list-item:not(.crm-list-item-selected):hover {
  background-color: #f8f9fa;
}

.crm-item-icon {
  margin-right: 0.5rem;
}

.crm-item-content {
  flex: 1;
}

.crm-item-title {
  font-weight: 600;
}

.crm-item-caption {
  color: #6c757d;
}

.crm-list-item-selected {
  background-color: #727cf5;
}

.crm-list-item-selected .crm-item-title,
.crm-list-item-selected .crm-item-caption,
.crm-list-item-selected i {
  color: white;
}
</style>
