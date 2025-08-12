<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />
    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col sm="5">
                <a href="javascript:void(0);" class="btn btn-danger mb-2"
                  ><i class="mdi mdi-plus-circle me-2"></i> Add Products</a
                >
              </b-col>
              <b-col sm="7">
                <div class="text-sm-end">
                  <button type="button" class="btn btn-success mb-2 me-1">
                    <i class="mdi mdi-cog-outline"></i>
                  </button>
                  <button type="button" class="btn btn-light mb-2 me-1">
                    Import
                  </button>
                  <button type="button" class="btn btn-light mb-2">
                    Export
                  </button>
                </div> </b-col
              ><!-- end col-->
            </b-row>

            <div class="table-responsive">
              <table
                class="table table-centered w-100 dt-responsive nowrap"
                id="products-datatable"
              >
                <thead class="table-light">
                  <tr>
                    <th class="all" style="width: 20px">
                      <div class="form-check">
                        <input
                          type="checkbox"
                          class="form-check-input"
                          id="customCheck1"
                        />
                        <label class="form-check-label" for="customCheck1"
                          >&nbsp;</label
                        >
                      </div>
                    </th>
                    <th class="all">Product</th>
                    <th>Category</th>
                    <th>Added Date</th>
                    <th>Price</th>
                    <th>Quantity</th>
                    <th>Status</th>
                    <th style="width: 85px">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(prod, index) in productData" :key="index">
                    <td>
                      <div class="form-check">
                        <input
                          type="checkbox"
                          class="form-check-input"
                          id="customCheck2"
                        />
                        <label class="form-check-label" for="customCheck2"
                          >&nbsp;</label
                        >
                      </div>
                    </td>
                    <td>
                      <img
                        :src="prod.image"
                        alt="contact-img"
                        title="contact-img"
                        class="rounded me-3"
                        height="48"
                      />
                      <p class="m-0 d-inline-block align-middle font-16">
                        <router-link
                          to="/apps/ecommerce/products-details"
                          class="text-body"
                          >{{ prod.name }}</router-link
                        >
                        <br />
                        <span
                          v-for="num in prod.rating"
                          class="text-warning mdi mdi-star"
                        ></span>
                      </p>
                    </td>
                    <td>
                      {{ prod.category }}
                    </td>
                    <td>
                      {{ prod.date }}
                    </td>
                    <td>
                      {{ prod.price }}
                    </td>

                    <td>
                      {{ prod.quantity }}
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="
                          prod.status == 'Active' ? 'bg-success' : 'bg-danger'
                        "
                        >{{ prod.status }}</span
                      >
                    </td>

                    <td class="table-action">
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-eye"></i
                      ></a>
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-square-edit-outline"></i
                      ></a>
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-delete"></i
                      ></a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- end card-body-->
        </div>
        <!-- end card-->
      </b-col>
      <!-- end col -->
    </b-row>
    <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import { productData } from "@/views/apps/ecommerce/products/data";
import BaseDataTable from "@/components/base-data-table.vue";

export default {
  components: { BaseDataTable, Breadcrumb, Layout },
  data() {
    return {
      title: "Products",
      items: [
        {
          text: "Hyper",
          href: "/",
        },
        {
          text: "eCommerce",
          href: "/",
        },
        {
          text: "Products",
          active: true,
        },
      ],
      productData,
    };
  },
  mounted() {
    $("#products-datatable").DataTable({
      language: {
        paginate: {
          previous: "<i class='mdi mdi-chevron-left'>",
          next: "<i class='mdi mdi-chevron-right'>",
        },
        info: "Showing products _START_ to _END_ of _TOTAL_",
        lengthMenu:
          "Display <select class='form-select form-select-sm ms-1 me-1'>" +
          '<option value="5">5</option>' +
          '<option value="10">10</option>' +
          '<option value="20">20</option>' +
          '<option value="-1">All</option>' +
          "</select> products",
      },
      pageLength: 5,
      columns: [
        {
          orderable: false,
          targets: 0,
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
              '<div class="form-check"><input type="checkbox" class="form-check-input dt-checkboxes"><label class="form-check-label">&nbsp;</label></div>',
          },
        },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: true },
        { orderable: false },
      ],
      select: {
        style: "multi",
      },
      order: [[1, "asc"]],
      drawCallback: function () {
        $(".dataTables_paginate > .pagination").addClass("pagination-rounded");
        $("#products-datatable_length label").addClass("form-label");

        // Col add & remove
        var filterDiv = document.querySelector(".dataTables_wrapper .row");
        filterDiv!.querySelectorAll(".col-md-6").forEach(function (element) {
          element.classList.add("col-sm-6");
          element.classList.remove("col-sm-12");
          element.classList.remove("col-md-6");
        });
      },
    });
  },
};
</script>
