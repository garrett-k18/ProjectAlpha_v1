<template>
  <!--
    Legal CRM Page
    Uses master CRMListView component with legal-specific configuration
    Component path: frontend_vue/src/views/apps/crm/legal/index_legalcrm.vue
  -->
  <Layout>
    <Breadcrumb :title="title" :items="breadcrumbItems"/>
    
    <CRMListView
      entity-type="Legal Contact"
      :columns="legalColumns"
      :filters="legalFilters"
      :data="store.results"
      :loading="store.loading"
      :error="store.error"
      add-button-text="Add Legal Contact"
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
import { useLegalStore } from '@/stores/legal';

export default defineComponent({
  name: 'LegalPage',
  
  components: {
    Layout,
    Breadcrumb,
    CRMListView,
  },

  data() {
    return {
      title: 'Legal Contacts',
      breadcrumbItems: [
        { text: 'Hyper', href: '/' },
        { text: 'CRM', href: '/' },
        { text: 'Legal', active: true },
      ],
      store: useLegalStore(),
    };
  },

  computed: {
    /**
     * Column configuration for legal contacts
     * What: Defines which fields to display in the CRM table
     * Why: Legal contacts need firm, name, email, phone, location
     * How: Maps to MasterCRM model fields via store
     */
    legalColumns() {
      return [
        {
          field: 'firm',
          header: 'Firm',
          editable: true,
          placeholder: 'Smith & Associates',
        },
        {
          field: 'name',
          header: 'Contact Name',
          editable: true,
          placeholder: 'John Smith',
        },
        {
          field: 'email',
          header: 'Email',
          editable: true,
          placeholder: 'john@smithlaw.com',
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
          placeholder: '(555) 123-4567',
          component: 'a',
          componentProps: (row: any) => ({
            href: `tel:${row.phone}`,
            class: 'text-primary text-decoration-underline',
          }),
        },
        {
          field: 'city',
          header: 'City',
          editable: true,
          placeholder: 'New York',
        },
        {
          field: 'state',
          header: 'State',
          editable: true,
          placeholder: 'NY',
        },
      ];
    },

    /**
     * Filter configuration for legal contacts
     * What: Defines available filter options
     * Why: Allow users to filter by state, search, etc.
     * How: Passed to CRMListView component
     */
    legalFilters() {
      // Extract unique states from loaded legal contacts
      const states = new Set<string>();
      this.store.results.forEach((legal: any) => {
        if (legal.state) states.add(legal.state);
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
     * Handle search
     * What: Triggers search when user types in search box
     * Why: Allow users to find specific legal contacts
     * How: Calls store.fetchLegal with search query
     */
    onSearch(query: string) {
      this.store.fetchLegal({ page: 1, q: query });
    },

    /**
     * Handle filter changes
     * What: Triggers filter when user selects filter options
     * Why: Allow users to narrow down legal contact list
     * How: Calls store.fetchLegal with filter params
     */
    onFilter(filters: any) {
      console.log('Filters:', filters);
      if (filters.state) {
        // TODO: Add state filter to API when available
        this.store.fetchLegal({ page: 1 });
      } else {
        this.store.fetchLegal({ page: 1 });
      }
    },

    /**
     * Handle create legal contact
     * What: Opens modal/form to create new legal contact
     * Why: Allow users to add new legal contacts to CRM
     * How: Calls store.createLegal with form data
     */
    onCreate(data: any) {
      console.log('Create legal contact:', data);
      this.store.createLegal(data).then((success) => {
        if (success) {
          console.log('Legal contact created successfully');
        }
      });
    },

    /**
     * Handle update legal contact
     * What: Opens modal/form to edit existing legal contact
     * Why: Allow users to modify legal contact information
     * How: Calls store.updateLegal with updated data
     */
    onUpdate(id: number, data: any) {
      console.log('Update legal contact:', id, data);
      this.store.updateLegal(id, data).then((success) => {
        if (success) {
          console.log('Legal contact updated successfully');
        }
      });
    },

    /**
     * Handle export legal contacts
     * What: Exports legal contact list to CSV/Excel
     * Why: Allow users to download legal contact data
     * How: Generates file from store.results
     */
    onExport() {
      console.log('Export legal contacts');
      // TODO: Implement export functionality
      const csv = this.store.results.map(item => 
        `${item.firm},${item.name},${item.email},${item.phone},${item.city},${item.state}`
      ).join('\n');
      
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'legal-contacts.csv';
      a.click();
    },
  },

  mounted() {
    // Fetch legal contacts on mount
    // What: Loads initial legal contact data when page loads
    // Why: Display legal contacts immediately when user navigates to page
    // How: Calls store.fetchLegal with page 1
    this.store.fetchLegal({ page: 1 });
  },
});
</script>

<style scoped>
/* Legal CRM specific styles if needed */
</style>
