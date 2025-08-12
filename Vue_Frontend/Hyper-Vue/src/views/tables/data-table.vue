<template>
  <Layout>
    <Breadcrumb title="Data Tables" subtitle="Tables"/>
    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Basic Data Table">
          <template v-slot:sub-text>
            DataTables has most features enabled by default, so all you need
            to do to use it with your own tables is to call the construction
            function:
            <code>$().DataTable();</code>. KeyTable provides Excel like cell
            navigation on any table. Events (focus, blur, action etc) can be
            assigned to individual cells, columns, rows or all cells.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="basic-datatable" class="table table-striped dt-responsive nowrap w-100"
                           :t-head="tableHead1"
                           :data="basicDatatable" :options="basicDatatableOptions"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Multi item selection">
          <template v-slot:sub-text>
            This example shows the multi option. Note how a click on a row
            will toggle its selected state without effecting other rows,
            unlike the os and single options shown in other examples.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="selection-datatable"
                           class="table table-striped dt-responsive nowrap w-100"
                           :data="selectionDatatable"
                           :options="selectionDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Alternative Pagination">
          <template v-slot:sub-text>
            The default page control presented by DataTables (forward and
            backward buttons with up to 7 page numbers in-between) is fine for
            most situations, but there are cases where you may wish to
            customise the options presented to the end user.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="alternative-page-datatable"
                           class="table table-striped dt-responsive nowrap w-100"
                           :data="alternativePageDatatable"
                           :options="alternativePageDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Scroll - Vertical">
          <template v-slot:sub-text>
            This example shows the DataTables table body scrolling in the
            vertical direction. This can generally be seen as an alternative
            method to pagination for displaying a large table in a fairly
            small vertical area, and as such pagination has been disabled here
            (note that this is not mandatory, it will work just fine with
            pagination enabled as well!).
          </template>

          <template v-slot:preview>
            <BaseDataTable id="scroll-vertical-datatable"
                           class="table table-striped dt-responsive nowrap w-100"
                           :data="scrollVerticalDatatable"
                           :options="scrollVerticalDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Scroll - Horizontal">
          <template v-slot:sub-text>
            DataTables has the ability to show tables with horizontal
            scrolling, which is very useful for when you have a wide table,
            but want to constrain it to a limited horizontal display area.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="scroll-horizontal-datatable"
                           class="table table-striped w-100 nowrap"
                           :data="scrollHorizontalDatatable"
                           :options="scrollHorizontalDatatableOptions"
                           :t-head="tableHead2"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Complex headers with column visibility">
          <template v-slot:sub-text>
            Complex headers (using <code>colspan</code> /
            <code>rowspan</code>) can be used to group columns of similar
            information in DataTables, creating a very powerful visual effect.
          </template>

          <template v-slot:preview>
            <DataTable
                id="complex-header-datatable"
                class="table table-striped dt-responsive nowrap w-100"
                :data="complexHeaderDatatable"
                :options="complexHeaderDatatableOptions"
            >
              <thead class="table-light">
              <tr>
                <th rowspan="2" class="align-middle">Name</th>
                <th colspan="2">HR Information</th>
                <th colspan="3">Contact</th>
              </tr>
              <tr>
                <th>Position</th>
                <th>Salary</th>
                <th>Office</th>
                <th>Extn.</th>
                <th>E-mail</th>
              </tr>
              </thead>
            </DataTable>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Row Created Callback">
          <template v-slot:sub-text>
            The following example shows how a callback function can be used to
            format a particular row at draw time. For each row that is
            generated for display, the createdRow function is called once and
            once only. It is passed the create row node which can then be
            modified.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="row-callback-datatable"
                           class="table table-striped dt-responsive nowrap w-100"
                           :data="rowCallbackDatatable"
                           :options="rowCallbackDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="State Saving">
          <template v-slot:sub-text>
            DataTables has the option of being able to save the state of a
            table (its paging position, ordering state etc) so that is can be
            restored when the user reloads a page, or comes back to the page
            after visiting a sub-page. This state saving ability is enabled by
            the stateSave option.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="state-saving-datatable"
                           class="table activate-select dt-responsive nowrap w-100"
                           :data="stateSavingDatatable"
                           :options="stateSavingDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Fixed Columns">
          <template v-slot:sub-text>
            When making use of DataTables' x-axis scrolling feature you may
            wish to fix the left or right most columns in place.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="fixed-columns-datatable"
                           class="table table-striped nowrap row-border order-column w-100"
                           :data="fixedColumnsDatatable"
                           :options="fixedColumnsDatatableOptions"
                           :t-head="tableHead2"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>

    <b-row>
      <b-col cols="12">

        <CustomSyntax title="Fixed Header">
          <template v-slot:sub-text>
            The FixedHeader will freeze in place the header and/or footer in a
            DataTable, ensuring that title information will remain always
            visible.
          </template>

          <template v-slot:preview>
            <BaseDataTable id="fixed-header-datatable"
                           class="table table-striped dt-responsive nowrap table-striped w-100"
                           :data="fixedHeaderDatatable"
                           :options="fixedHeaderDatatableOptions"
                           :t-head="tableHead1"/>
          </template>
        </CustomSyntax>

      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {tableData2} from "./data";
import BaseDataTable from "@/components/base-data-table.vue";

declare global {
  interface Window {
    jQuery: any;
    $: any;
    dt: any;
  }
}

import jQuery from "jquery";

window.$ = window.jQuery = jQuery;
import dataTables from "datatables.net";

window.dt = dataTables;

import DataTable from "datatables.net-vue3";
import DataTablesCore from "datatables.net";

// import "datatables.net-responsive-bs5/css/responsive.bootstrap5.min.css"
// import "datatables.net-buttons-bs5/css/buttons.bootstrap5.min.css"
import "datatables.net-bs5/css/dataTables.bootstrap5.min.css";
import "datatables.net-bs5";
import CustomSyntax from "@/components/custom/custom-syntax.vue";

// import "datatables.net-buttons-bs5/js/buttons.bootstrap5.min.js"
// import "datatables.net-buttons/js/buttons.html5.min.js"
// import "datatables.net-buttons/js/buttons.flash.min.js"
// import "datatables.net-buttons/js/buttons.print.min.js"
// import "datatables.net-keytable/js/dataTables.keyTable.min.js"

DataTable.use(DataTablesCore);

export default {
  components: {CustomSyntax, BaseDataTable, Layout, Breadcrumb, DataTable},
  data() {
    return {
      tableData: tableData2,
      tableHead1: ['Name', 'Position', 'Office', 'Age', 'Start Date', 'Salary'],
      tableHead2: ['First name', 'Last name', 'Position', 'Office', 'Age', 'Start Date', 'Salary', 'Extn.', 'E-mail'],
      basicDatatable: [] as {}[],
      datatableButtons: [] as {}[],
      selectionDatatable: [] as {}[],
      alternativePageDatatable: [] as {}[],
      scrollVerticalDatatable: [] as {}[],
      scrollHorizontalDatatable: [] as {}[],
      complexHeaderDatatable: [] as {}[],
      rowCallbackDatatable: [] as {}[],
      stateSavingDatatable: [] as {}[],
      fixedColumnsDatatable: [] as {}[],
      fixedHeaderDatatable: [] as {}[],

      basicDatatableOptions: {
        keys: true,
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
      },
      datatableButtonsOptions: {
        lengthChange: false,
        buttons: ['copy', 'print'],
        language: {
          "paginate": {
            "previous": "<i class='mdi mdi-chevron-left'>",
            "next": "<i class='mdi mdi-chevron-right'>"
          }
        },
        drawCallback: this.drawCallback,
      },
      selectionDatatableOptions: {
        select: {
          style: 'multi'
        },
        language: {
          "paginate": {
            "previous": "<i class='mdi mdi-chevron-left'>",
            "next": "<i class='mdi mdi-chevron-right'>"
          }
        },
        drawCallback: this.drawCallback,
      },
      alternativePageDatatableOptions: {
        pagingType: "full_numbers",
        drawCallback: this.drawCallback,
      },
      scrollVerticalDatatableOptions: {
        scrollY: "350px",
        scrollCollapse: true,
        paging: false,
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
      },
      scrollHorizontalDatatableOptions: {
        scrollX: true,
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
      },
      complexHeaderDatatableOptions: {
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
        columnDefs: [
          {
            visible: false,
            targets: -1,
          },
        ],
      },
      rowCallbackDatatableOptions: {
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
        createdRow: this.createdRow,
      },
      stateSavingDatatableOptions: {
        stateSave: true,
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
      },
      fixedColumnsDatatableOptions: {
        scrollY: 300,
        scrollX: true,
        scrollCollapse: true,
        paging: false,
        fixedColumns: true,
      },
      fixedHeaderDatatableOptions: {
        responsive: true,
        language: {
          paginate: {
            previous: "<i class='ri-arrow-left-s-line'>",
            next: "<i class='ri-arrow-right-s-line'>",
          },
        },
        drawCallback: this.drawCallback,
      },
    };
  },
  mounted() {

    this.basicDatatable =
        this.datatableButtons =
            this.selectionDatatable =
                this.alternativePageDatatable =
                    this.scrollVerticalDatatable =
                        this.rowCallbackDatatable =
                            this.stateSavingDatatable =
                                this.fixedHeaderDatatable =
                                    this.tableData.map((i) => [
                                      i.Name,
                                      i.Position,
                                      i.Office,
                                      i.Age,
                                      i.Start_date,
                                      i.Salary,
                                    ]);

    this.scrollHorizontalDatatable = this.fixedColumnsDatatable = this.tableData.map(
        (i) => [
          i.First_name,
          i.Last_name,
          i.Position,
          i.Office,
          i.Age,
          i.Start_date,
          i.Salary,
          i.Extn,
          i.E_mail,
        ]
    );

    this.complexHeaderDatatable = this.tableData.map((i) => [
      i.Name,
      i.Position,
      i.Salary,
      i.Office,
      i.Extn,
      i.E_mail,
    ]);
  },
  methods: {
    drawCallback() {
      $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
    },
    createdRow(row: any, data: any, index: number) {
      if (data[5].replace(/[\$,]/g, "") * 1 > 150000) {
        $("td", row).eq(5).addClass("text-danger");
      }
    },
  },
};
</script>
