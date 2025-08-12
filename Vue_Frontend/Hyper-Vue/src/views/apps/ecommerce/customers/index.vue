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
                  Customers</a>
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
              <table class="table table-centered table-striped dt-responsive nowrap w-100" id="products-datatable">
                <thead>
                <tr>
                  <th style="width: 20px;">
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck1">
                      <label class="form-check-label" for="customCheck1">&nbsp;</label>
                    </div>
                  </th>
                  <th>Customer</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Location</th>
                  <th>Create Date</th>
                  <th>Status</th>
                  <th style="width: 75px;">Action</th>
                </tr>
                </thead>
                <tbody>

                <tr v-for="(customer,index) in customersData">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck2">
                      <label class="form-check-label" for="customCheck2">&nbsp;</label>
                    </div>
                  </td>
                  <td class="table-user">
                    <img :src="customer.image" alt="table-user" class="me-2 rounded-circle">
                    <a href="javascript:void(0);" class="text-body fw-semibold">{{ customer.name }}</a>
                  </td>
                  <td>
                    {{ customer.phone }}
                  </td>
                  <td>
                    {{ customer.email }}
                  </td>
                  <td>
                    {{ customer.location }}
                  </td>
                  <td>
                    {{ customer.date }}
                  </td>
                  <td>
                    <span class="badge badge-success-lighten" :class="customer.status == 'Active' ? 'badge-success-lighten' : 'badge-danger-lighten' ">{{ customer.status }}</span>
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

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import {customersData} from "@/views/apps/ecommerce/customers/data";

import BaseDataTable from "@/components/base-data-table.vue";

export default {

  components: {Breadcrumb, Layout,BaseDataTable},
  data() {
    return {
      title: 'Products',
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
          text: 'Products',
          active: true,
        },
      ],
      customersData
    }
  },
  mounted() {
    $("#products-datatable").DataTable({
      language: {
        paginate: {
          previous: "<i class='mdi mdi-chevron-left'>",
          next: "<i class='mdi mdi-chevron-right'>"
        },
        info: "Showing customers _START_ to _END_ of _TOTAL_",
        lengthMenu:
            "Display <select class='form-select form-select-sm ms-1 me-1'>" +
            '<option value="10">10</option>' +
            '<option value="20">20</option>' +
            '<option value="-1">All</option>' +
            "</select> customers"
      },
      columnDefs: [
        {
          targets: -1,
          className: 'dt-body-right'
        }],
      pageLength: 10,
      columns: [
        {
          orderable: false,
          render: function (data, type, row, meta) {
            if (type === "display") {
              data =
                  '<div class="form-check"><input type="checkbox" class="form-check-input dt-checkboxes"><label class="form-check-label">&nbsp;</label></div>';
            }
            return data;
          },
          checkboxes: {
            selectRow: true,
            selectAllRender:
                '<div class="form-check"><input type="checkbox" class="form-check-input dt-checkboxes"><label class="form-check-label">&nbsp;</label></div>'
          }
        },
        {orderable: true},
        {orderable: true},
        {orderable: true},
        {orderable: true},
        {orderable: true},
        {orderable: true},
        {orderable: false}
      ],
      select: {
        style: "multi"
      },
      order: [[5, "asc"]],
      drawCallback: function () {
        $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
        $('#products-datatable_length label').addClass('form-label');


        // Col add & remove
        var filterDiv = document.querySelector('.dataTables_wrapper .row');
        filterDiv!.querySelectorAll('.col-md-6').forEach(function (element) {
          element.classList.add('col-sm-6');
          element.classList.remove('col-sm-12');
          element.classList.remove('col-md-6');
        });
      }
    });
  }

}
</script>
