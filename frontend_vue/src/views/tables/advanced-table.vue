<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Advanced Table">
          <template v-slot:sub-text>

          </template>
          <template v-slot:preview>
            <b-row class="mb-md-2">
              <b-col sm="12" md="6">
                <div id="tickets-table_length" class="dataTables_length">
                  <label class="d-inline-flex align-items-center">
                    Show&nbsp;
                    <b-form-select v-model="perPage" size="sm" :options="pageOptions"></b-form-select>&nbsp;entries
                  </label>
                </div>
              </b-col>
              <!-- Search -->
              <b-col sm="12" md="6">
                <div id="tickets-table_filter" class="dataTables_filter text-md-end">
                  <label class="d-inline-flex align-items-center">
                    Search:
                    <b-form-input
                        v-model="filter"
                        type="search"
                        placeholder="Search..."
                        class="form-control form-control-sm ms-2"
                    ></b-form-input>
                  </label>
                </div>
              </b-col>
              <!-- End search -->
            </b-row>
            <!-- Table -->
            <div class="table-responsive mb-0">
              <b-table
                  :items="tableData"
                  :fields="fields"
                  responsive="sm"
                  :per-page="perPage"
                  :current-page="currentPage"
                  :sort-by.sync="sortBy"
                  :sort-desc.sync="sortDesc"
                  :filter="filter"
                  :filter-included-fields="filterOn"
                  @filtered="onFiltered"
              ></b-table>
            </div>
            <b-row>
              <b-col>
                <div class="dataTables_paginate paging_simple_numbers float-end">
                  <ul class="pagination pagination-rounded mb-0">
                    <!-- pagination -->
                    <b-pagination v-model="currentPage" :total-rows="rows" :per-page="perPage"></b-pagination>
                  </ul>
                </div>
              </b-col>
            </b-row>
          </template>
        </CustomSyntax>

      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->
  </Layout>
</template>
<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import { tableData1 } from './data'
import CustomSyntax from "@/components/custom/custom-syntax.vue";

export default {
  components: {CustomSyntax, Layout, Breadcrumb },
  data() {
    return {
      title: 'Advanced Table',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Tables',
          href: '/',
        },
        {
          text: 'Advanced Tables',
          active: true,
        },
      ],
      tableData: tableData1,
      totalRows: 1,
      currentPage: 1,
      perPage: 10,
      pageOptions: [10, 25, 50, 100],
      filter:'',
      filterOn: [],
      sortBy: 'age',
      sortDesc: false,
      fields: [
        { key: 'name', sortable: true },
        { key: 'position', sortable: true },
        { key: 'office', sortable: true },
        { key: 'age', sortable: true },
        { key: 'date', sortable: true },
        { key: 'salary', sortable: true },
      ],
    }
  },
  computed: {
    /**
     * Total no. of records
     */
    rows() {
      return this.tableData.length
    },
  },
  mounted() {
    // Set the initial number of items
    this.totalRows = this.items.length
  },
  methods: {
    /**
     * Search the table data with search input
     */
    onFiltered(filteredItems:[]) {
      // Trigger pagination to update the number of buttons/pages due to filtering
      this.totalRows = filteredItems.length
      this.currentPage = 1
    },
  },
}
</script>