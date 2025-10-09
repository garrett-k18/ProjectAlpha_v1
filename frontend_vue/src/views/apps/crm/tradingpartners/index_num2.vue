<template>
  <!--
    Trading Partners CRM Page
    Uses master CRMListView component with trading partner-specific configuration
    Component path: frontend_vue/src/views/apps/crm/tradingpartners/index_num2.vue
  -->
  <Layout>
    <Breadcrumb :title="title" :items="breadcrumbItems"/>
    
    <CRMListView
      entity-type="Trading Partner"
      :columns="partnerColumns"
      :filters="partnerFilters"
      :data="store.results"
      :loading="store.loading"
      :error="store.error"
      add-button-text="Add Trading Partner"
      @search="onSearch"
      @filter="onFilter"
      @create="onCreate"
      @update="onUpdate"
      @export="onExport"
      @view-nda="onViewNDA"
    />
  </Layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import CRMListView from "@/views/apps/crm/components/index_mastercrm.vue";
import { useTradingPartnersStore } from '@/stores/tradingPartners';

export default defineComponent({
  name: 'TradingPartnersPage',
  
  components: {
    Layout,
    Breadcrumb,
    CRMListView,
  },

  data() {
    return {
      title: 'Trading Partners',
      breadcrumbItems: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Trading Partners', active: true },
      ],
      store: useTradingPartnersStore(),
    };
  },

  computed: {
    /**
     * Column configuration for trading partners
     */
    partnerColumns() {
      return [
        {
          field: 'firm',
          header: 'Firm',
          editable: true,
          placeholder: 'ABC Capital Partners',
          component: 'router-link',
          componentProps: (row: any) => ({
            to: `/acq/trading-partners/${row.id}`,
            class: 'text-body fw-bold',
          }),
        },
        {
          field: 'name',
          header: 'Primary Contact',
          editable: true,
          placeholder: 'John Smith',
        },
        {
          field: 'email',
          header: 'Email',
          editable: true,
          inputType: 'email',
          placeholder: 'john@example.com',
        },
        {
          field: 'phone',
          header: 'Phone',
          editable: true,
          inputType: 'tel',
          placeholder: '(555) 123-4567',
          formatter: (row: any) => this.formatPhone(row.phone),
        },
        {
          field: 'nda_flag',
          header: 'NDA Signed',
          component: 'div',
          componentProps: (row: any) => ({
            class: 'form-check',
          }),
          formatter: (row: any) => '',  // Custom rendering in template
          customRender: true,  // Flag for custom cell rendering
        },
        {
          field: 'nda_signed',
          header: 'Date Signed',
          formatter: (row: any) => row.nda_signed ? this.formatDate(row.nda_signed) : '—',
        },
      ];
    },

    /**
     * Filter configuration for trading partners
     */
    partnerFilters() {
      return [
        {
          field: 'nda',
          label: 'NDA Status',
          options: ['Signed', 'Not Signed'],
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
     * Format date to readable format
     */
    formatDate(dateStr: string | null): string {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
      } catch {
        return dateStr;
      }
    },

    /**
     * Handle search
     */
    onSearch(query: string) {
      this.store.fetchPartners({ page: 1, q: query });
    },

    /**
     * Handle filter change
     */
    onFilter(filters: Record<string, string>) {
      console.log('Filters:', filters);
      // TODO: Implement NDA filter when backend supports it
      this.store.fetchPartners({ page: 1 });
    },

    /**
     * Handle page change
     */
    onPageChange(page: number) {
      this.store.fetchPartners({ page });
    },

    /**
     * Handle create trading partner
     */
    async onCreate(data: any) {
      const payload = {
        firm: data.firm || null,
        name: data.name || null,
        email: data.email || null,
        phone: data.phone || null,
        tag: 'trading_partner',  // Set MasterCRM tag to trading_partner
      };
      await this.store.createPartner(payload);
    },

    /**
     * Handle update trading partner
     */
    async onUpdate(payload: { id: number; data: any }) {
      const data = {
        firm: payload.data.firm || null,
        name: payload.data.name || null,
        email: payload.data.email || null,
        phone: payload.data.phone || null,
      };
      await this.store.updatePartner(payload.id, data);
    },

    /**
     * Handle view NDA document
     * Connects to Egnyte document database API
     */
    async onViewNDA(partner: any) {
      if (!partner.nda_flag) {
        alert('No NDA on file for this trading partner.');
        return;
      }
      
      try {
        // TODO: Replace with actual Egnyte API endpoint
        // const response = await http.get(`/api/documents/nda/${partner.id}`);
        // const egnyteUrl = response.data.egnyte_url;
        // window.open(egnyteUrl, '_blank');
        
        console.log('Fetching NDA document from Egnyte for partner:', partner.id);
        alert(`NDA document viewer will open here. Partner: ${partner.firm}\nEgnyte API integration pending.`);
      } catch (error) {
        console.error('Failed to fetch NDA document:', error);
        alert('Failed to load NDA document. Please try again.');
      }
    },

    /**
     * Handle export
     */
    onExport() {
      console.log('Export trading partners');
      // Implement export logic
    },
  },

  mounted() {
    // Fetch trading partners on mount
    this.store.fetchPartners({ page: 1 });
  },
});
</script>
