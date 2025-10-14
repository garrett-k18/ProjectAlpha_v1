<template>
  <!--
    Investors CRM Page
    Uses master CRMListView component with investor-specific configuration
    Component path: frontend_vue/src/views/apps/crm/investors/index_investorcrm.vue
  -->
  <Layout>
    <Breadcrumb :title="title" :items="breadcrumbItems"/>
    
    <CRMListView
      entity-type="Investor"
      :columns="investorColumns"
      :filters="investorFilters"
      :data="store.results"
      :loading="store.loading"
      :error="store.error"
      add-button-text="Add Investor"
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
import { useInvestorsStore } from '@/stores/investors';

export default defineComponent({
  name: 'InvestorsPage',
  
  components: {
    Layout,
    Breadcrumb,
    CRMListView,
  },

  data() {
    return {
      title: 'Investors',
      breadcrumbItems: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Investors', active: true },
      ],
      store: useInvestorsStore(),
    };
  },

  computed: {
    /**
     * Column configuration for investors
     */
    investorColumns() {
      return [
        {
          field: 'firm',
          header: 'Firm',
          editable: true,
          placeholder: 'Alpha Capital Partners',
          component: 'router-link',
          componentProps: (row: any) => ({
            to: `/acq/investors/${row.id}`,
            class: 'text-body',
          }),
        },
        {
          field: 'name',
          header: 'Contact Name',
          editable: true,
          placeholder: 'Sarah Johnson',
        },
        {
          field: 'email',
          header: 'Email',
          editable: true,
          inputType: 'email',
          placeholder: 'sarah@example.com',
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
     * Filter configuration for investors
     */
    investorFilters() {
      // Build unique states from current results
      const states = new Set<string>();
      this.store.results.forEach((investor: any) => {
        if (investor.state) states.add(investor.state);
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
      this.store.fetchInvestors({ page: 1, q: query });
    },

    /**
     * Handle filter change
     */
    onFilter(filters: Record<string, string>) {
      console.log('Filters:', filters);
      if (filters.state) {
        // TODO: Add state filter to API when available
        this.store.fetchInvestors({ page: 1 });
      } else {
        this.store.fetchInvestors({ page: 1 });
      }
    },

    /**
     * Handle create investor
     */
    async onCreate(data: any) {
      const payload = {
        firm: data.firm || null,
        name: data.name || null,
        email: data.email || null,
        phone: data.phone || null,
        city: data.city || null,
        state: data.state || null,
        tag: 'investor',  // Set MasterCRM tag to investor
      };
      await this.store.createInvestor(payload);
    },

    /**
     * Handle update investor
     */
    async onUpdate(payload: { id: number; data: any }) {
      const data = {
        firm: payload.data.firm || null,
        name: payload.data.name || null,
        email: payload.data.email || null,
        phone: payload.data.phone || null,
        city: payload.data.city || null,
        state: payload.data.state || null,
      };
      await this.store.updateInvestor(payload.id, data);
    },

    /**
     * Handle export
     */
    onExport() {
      console.log('Export investors');
      // Implement export logic
    },
  },

  mounted() {
    // Fetch investors on mount
    this.store.fetchInvestors({ page: 1 });
  },
});
</script>
