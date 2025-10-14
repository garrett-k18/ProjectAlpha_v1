<template>
  <!--
    Brokers CRM Page
    Uses master CRMListView component with broker-specific configuration
    Component path: frontend_vue/src/views/apps/crm/brokers/index_brokercrm.vue
  -->
  <Layout>
    <Breadcrumb :title="title" :items="breadcrumbItems"/>
    
    <CRMListView
      entity-type="Broker"
      :columns="brokerColumns"
      :filters="brokerFilters"
      :data="store.results"
      :loading="store.loading"
      :error="store.error"
      add-button-text="Add Broker"
      @search="onSearch"
      @filter="onFilter"
      @create="onCreate"
      @update="onUpdate"
      @export="onExport"
    />
  </Layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CRMListView from "@/views/apps/crm/components/index_mastercrm.vue";
import { useBrokersCrmStore } from '@/stores/brokerscrm';

export default defineComponent({
  name: 'BrokersPage',
  
  components: {
    Layout,
    Breadcrumb,
    CRMListView,
  },

  data() {
    return {
      title: 'Brokers',
      breadcrumbItems: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Brokers', active: true },
      ],
      store: useBrokersCrmStore(),
    };
  },

  computed: {
    /**
     * Column configuration for brokers
     */
    brokerColumns() {
      return [
        {
          field: 'firm',
          header: 'Brokerage',
          editable: true,
          placeholder: 'ABC Realty',
        },
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
            const city = row.city || '';
            const state = row.state || '';
            if (city && state) return `${city}, ${state}`;
            return city || state || '—';
          },
        },
        {
          field: 'state',
          header: 'State',
          editable: true,
          placeholder: 'TX',
          maxlength: 2,
          transform: (val: string) => (val || '').toUpperCase().slice(0, 2),
          cols: 4,
          md: 3,
        },
         {
          field: 'email',
          header: 'Email',
          editable: true,
          inputType: 'email',
          placeholder: 'jane@example.com',
          formatter: (row: any) => {
            if (!row.email) return '—';
            return row.email;
          },
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
          formatter: (row: any) => this.formatPhone(row.phone),
          component: 'a',
          componentProps: (row: any) => ({
            href: `tel:${row.phone}`,
            class: 'text-primary text-decoration-underline',
          }),
        },
      ];
    },

    /**
     * Filter configuration for brokers
     */
    brokerFilters() {
      // Build unique states from current results
      const states = new Set<string>();
      this.store.results.forEach((broker: any) => {
        if (broker.state) states.add(broker.state);
      });

      return [
        {
          field: 'state',
          label: 'State',
          options: Array.from(states).sort(),
        },
      ];
    },
  },

  methods: {
    /**
     * Format phone number to (xxx) xxx-xxxx
     */
    formatPhone(phone: string | null): string {
      const digits = (phone || '').replace(/\D/g, '');
      if (digits.length === 10) {
        const area = digits.slice(0, 3);
        const mid = digits.slice(3, 6);
        const last = digits.slice(6);
        return `(${area}) ${mid}-${last}`;
      }
      return phone || '—';
    },

    /**
     * Handle search
     */
    onSearch(query: string) {
      console.log('Search:', query);
      // Implement search logic with store
    },

    /**
     * Handle filter change
     */
    onFilter(filters: Record<string, string>) {
      console.log('Filters:', filters);
      if (filters.state) {
        this.store.fetchBrokers({ page: 1, state: filters.state });
      } else {
        this.store.fetchBrokers({ page: 1 });
      }
    },

    /**
     * Handle create broker
     */
    async onCreate(data: any) {
      const payload = {
        name: data.name || null,
        email: data.email || null,
        phone: data.phone || null,
        firm: data.firm || null,
        city: data.city || null,
        state: data.state || null,
        tag: 'broker',  // Set MasterCRM tag to broker
      };
      await this.store.createBroker(payload);
    },

    /**
     * Handle update broker
     */
    async onUpdate(payload: { id: number; data: any }) {
      const data = {
        name: payload.data.name || null,
        email: payload.data.email || null,
        phone: payload.data.phone || null,
        firm: payload.data.firm || null,
        city: payload.data.city || null,
        state: payload.data.state || null,
      };
      await this.store.updateBroker(payload.id, data);
    },

    /**
     * Handle export
     */
    onExport() {
      console.log('Export brokers');
      // Implement export logic
    },
  },

  mounted() {
    // Fetch brokers on mount
    this.store.fetchBrokers({ page: 1 });
  },
});
</script>
