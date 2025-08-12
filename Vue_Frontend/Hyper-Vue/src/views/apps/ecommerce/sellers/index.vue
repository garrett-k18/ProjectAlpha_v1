<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col sm="5">
                <a href="javascript:void(0);" class="btn btn-danger mb-2"><i class="mdi mdi-plus-circle me-2"></i> Add
                  Sellers</a>
              </b-col>
              <b-col sm="7">
                <div class="text-sm-end">
                  <button type="button" class="btn btn-success mb-2 me-1"><i class="mdi mdi-cog"></i></button>
                  <button type="button" class="btn btn-light mb-2 me-1">Import</button>
                  <button type="button" class="btn btn-light mb-2">Export</button>
                </div>
              </b-col><!-- end col-->
            </b-row>

            <div class="table-responsive">
              <table class="table table-centered table-borderless table-hover w-100 dt-responsive nowrap"
                     id="sellers-datatable">
                <thead class="table-light">
                <tr>
                  <th style="width: 20px;">
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck1">
                      <label class="form-check-label" for="customCheck1">&nbsp;</label>
                    </div>
                  </th>
                  <th>Seller</th>
                  <th>Store Name</th>
                  <th>Products</th>
                  <th>Wallet Balance</th>
                  <th>Create Date</th>
                  <th>Revenue</th>
                  <th style="width: 75px;">Action</th>
                </tr>
                </thead>
                <tbody>

                <tr v-for="(seller,index) in sellersData" :key="index">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck2">
                      <label class="form-check-label" for="customCheck2">&nbsp;</label>
                    </div>
                  </td>
                  <td class="table-user">
                    <img :src="seller.image" alt="table-user" class="me-2 rounded-circle">
                    <a href="javascript:void(0);" class="text-body fw-semibold">{{ seller.name }}</a>
                  </td>
                  <td>
                    {{ seller.storename }}
                  </td>
                  <td>
                    <span class="fw-semibold">{{ seller.products }}</span>
                  </td>
                  <td>
                    {{ seller.balance }}
                  </td>
                  <td>
                    {{ seller.date }}
                  </td>
                  <td>
                    <div class="spark-chart" :data-dataset="seller.series"></div>
                  </td>

                  <td>
                    <a href="javascript:void(0);" class="action-icon"> <i class="mdi mdi-square-edit-outline"></i></a>
                    <a href="javascript:void(0);" class="action-icon"> <i class="mdi mdi-delete"></i></a>
                  </td>
                </tr>

                </tbody>
              </table>
            </div>
          </div> <!-- end card-body-->
        </div> <!-- end card-->
      </b-col> <!-- end col -->
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import {sellersData} from "@/views/apps/ecommerce/sellers/data";
import BaseDataTable from "@/components/base-data-table.vue";

import ApexCharts from 'apexcharts'

export default {
  components: {Breadcrumb, Layout, BaseDataTable},
  data() {

    return {
      title: 'Sellers',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'eCommerce',
          href: '/',
        },
        {
          text: 'Sellers',
          active: true,
        },
      ],
      sellersData,

      options: {
        chart: {
          type: 'line',
          width: 80,
          height: 35,
          sparkline: {
            enabled: true
          }
        },
        series: [],
        stroke: {
          width: 2,
          curve: 'smooth'
        },
        markers: {
          size: 0
        },
        colors: ["#727cf5"],
        tooltip: {
          fixed: {
            enabled: false
          },
          x: {
            show: false
          },
          y: {
            title: {
              formatter: function () {
                return ''
              }
            }
          },
          marker: {
            show: false
          }
        }
      }
    }
  },
  mounted() {
    let charts:[] = []
    let options = this.options
    $('#sellers-datatable').DataTable({
      "language": {
        "paginate": {
          "previous": "<i class='mdi mdi-chevron-left'>",
          "next": "<i class='mdi mdi-chevron-right'>"
        },
        "info": "Showing sellers _START_ to _END_ of _TOTAL_",
        "lengthMenu": "Display <select class='form-select form-select-sm ms-1 me-1'>" +
            '<option value="10">10</option>' +
            '<option value="20">20</option>' +
            '<option value="-1">All</option>' +
            '</select> sellers',
      },
      "pageLength": 10,
      "columns": [
        {
          'orderable': false,
          'render': function (data, type, row, meta) {
            if (type === 'display') {
              data = "<div class=\"form-check\"><input type=\"checkbox\" class=\"form-check-input dt-checkboxes\"><label class=\"form-check-label\">&nbsp;</label></div>";
            }
            return data;
          },
          'checkboxes': {
            'selectRow': true,
            'selectAllRender': '<div class=\"form-check\"><input type=\"checkbox\" class=\"form-check-input dt-checkboxes\"><label class=\"form-check-label\">&nbsp;</label></div>'
          }
        },
        {'orderable': true},
        {'orderable': true},
        {'orderable': true},
        {'orderable': true},
        {'orderable': true},
        {'orderable': false},
        {'orderable': false}
      ],
      "select": {
        "style": "multi"
      },
      "order": [[4, "desc"]],
      "drawCallback": function () {

        $('.dataTables_paginate > .pagination').addClass('pagination-rounded');
        $('#sellers-datatable_length label').addClass('form-label');
        // {data: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54]}

        // remove existing charts
        if (charts.length > 0) {
          for (let idx = 0; idx < charts.length; idx++) {
            try {
              charts[idx].destroy();
            } catch (e) {
              console.log(e)
            };
          }
          charts = [];
        }

        $(".spark-chart").each(function (index) {
          let data = $(this).data()['dataset'].split(",");
          let series = []
          for (let i = 0; i < data.length; i++) {
            series.push(parseInt(data[i]))
          }
          options['series'] = [{'data': series}];
          let chart = new ApexCharts($(this)[0], options)
          charts.push(chart);
          chart.render();
        });

        // Col add & remove
        let filterDiv = document.querySelector('.dataTables_wrapper .row');
        filterDiv!.querySelectorAll('.col-md-6').forEach(function (element) {
          element.classList.add('col-sm-6');
          element.classList.remove('col-sm-12');
          element.classList.remove('col-md-6');
        });
      },
    });
  }

}
</script>
