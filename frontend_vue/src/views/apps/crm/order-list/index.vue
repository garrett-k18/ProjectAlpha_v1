<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col cols="12" >
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col xl="8">
                <b-form class="row gy-2 gx-2 align-items-center justify-content-xl-start justify-content-between">
                  <b-col class="col-auto">
                    <label for="inputPassword2" class="visually-hidden">Search</label>
                    <input type="search" class="form-control" id="inputPassword2" placeholder="Search...">
                  </b-col>
                  <b-col class="col-auto">
                    <div class="d-flex align-items-center">
                      <label for="status-select" class="me-2">Status</label>
                      <select class="form-select" id="status-select">
                        <option selected>Choose...</option>
                        <option value="1">Paid</option>
                        <option value="2">Awaiting Authorization</option>
                        <option value="3">Payment Failed</option>
                        <option value="4">Cash On Delivery</option>
                        <option value="5">Fulfilled</option>
                        <option value="6">Unfulfilled</option>
                      </select>
                    </div>
                  </b-col>
                </b-form>
              </b-col>
              <b-col xl="4">
                <div class="text-xl-end mt-xl-0 mt-2">
                  <button type="button" class="btn btn-danger mb-2 me-2"><i class="mdi mdi-basket me-1"></i> Add New
                    Order
                  </button>
                  <button type="button" class="btn btn-light mb-2">Export</button>
                </div>
              </b-col><!-- end col-->
            </b-row>

            <div class="table-responsive">
              <table class="table table-centered table-nowrap mb-0">
                <thead class="table-light">
                <tr>
                  <th style="width: 20px;">
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck1">
                      <label class="form-check-label" for="customCheck1">&nbsp;</label>
                    </div>
                  </th>
                  <th>Order ID</th>
                  <th>Customers</th>
                  <th>Project</th>
                  <th>Address</th>
                  <th>Date Order</th>
                  <th>Order Status</th>
                  <th style="width: 125px;">Action</th>
                </tr>
                </thead>
                <tbody>

                <tr v-for="(order, index) in orderData" :key="index">
                  <td>
                    <div class="form-check">
                      <input type="checkbox" class="form-check-input" id="customCheck2">
                      <label class="form-check-label" for="customCheck2">&nbsp;</label>
                    </div>
                  </td>
                  <td><a href="/apps/ecommerce/orders-details" class="text-body fw-bold">{{ order.id }}</a></td>
                  <td>
                    <div class="d-flex">
                      <div class="d-flex align-items-center">
                        <div class="flex-shrink-0">
                          <img :src="order.img" class="rounded-circle avatar-xs" alt="friend">
                        </div>
                        <div class="flex-grow-1 ms-2"><h5 class="my-0">{{ order.name }}</h5></div>
                      </div>
                    </div>
                  </td>
                  <td>{{ order.project }}</td>
                  <td>
                    <h5 class="my-0">{{ order.address.city }}</h5>
                    <p class="mb-0 txt-muted">{{ order.address.area }}</p>
                  </td>
                  <td>{{ order.date }}</td>
                  <td><h5 class="my-0"><span class="badge "
                                             :class="order.orderStatus == 'In Progress'?'badge-info-lighten': ''||order.orderStatus == 'Complete'?'badge-success-lighten': ''||order.orderStatus == 'Pending'?'badge-warning-lighten': ''||order.orderStatus == 'Delivered'?'badge-primary-lighten': ''"
                  >{{ order.orderStatus }}</span></h5></td>
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
    </b-row> <!-- end row -->
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {orderData} from "@/views/apps/crm/order-list/data";

export default {
  components: {Breadcrumb, Layout},
  data() {
    return {
      title: 'Orders List',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'CRM',
          href: '/',
        },
        {
          text: 'Orders List',
          active: true,
        },
      ],
      orderData
    }
  }
}
</script>
