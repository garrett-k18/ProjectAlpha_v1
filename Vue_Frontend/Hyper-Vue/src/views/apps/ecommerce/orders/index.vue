<template>
  <Layout>
    <Breadcrumb :title="title" :items="items" />

    <b-row>
      <b-col cols="12">
        <div class="card">
          <div class="card-body">
            <b-row class="mb-2">
              <b-col xl="8">
                <b-form
                  class="row gy-2 gx-2 align-items-center justify-content-xl-start justify-content-between"
                >
                  <b-col class="col-auto">
                    <b-form-group
                      class="visually-hidden"
                      label="Search"
                    ></b-form-group>

                    <b-form-input
                      type="search"
                      id="inputPassword2"
                      placeholder="Search..."
                    />
                  </b-col>
                  <b-col class="col-auto">
                    <div class="d-flex align-items-center">
                      <label for="status-select" class="me-2">Status</label>
                      <select class="form-select" id="status-select">
                        <option selected>Choose...</option>
                        <option value="1">Paid</option>
                        <option value="2">Awaiting Authorization</option>
                        <option value="3">Payment failed</option>
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
                  <b-button variant="danger" class="mb-2 me-2">
                    <i class="mdi mdi-basket me-1"></i> Add New Order
                  </b-button>
                  <b-button variant="light" class="mb-2"> Export </b-button>
                </div>
              </b-col>
              <!-- end col-->
            </b-row>

            <div class="table-responsive">
              <table class="table table-centered table-nowra mb-0">
                <thead class="table-light">
                  <tr>
                    <th style="width: 20px">
                      <b-form-checkbox value="&nbsp;"> </b-form-checkbox>
                    </th>
                    <th>Order ID</th>
                    <th>Date</th>
                    <th>Payment Status</th>
                    <th>Total</th>
                    <th>Payment Method</th>
                    <th>Order Status</th>
                    <th style="width: 125px">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(order, index) of orderData" :key="order.id">
                    <td>
                      <div class="form-check">
                        <input
                          :id="`customCheck${index}`"
                          type="checkbox"
                          class="form-check-input"
                        />
                        <label
                          class="form-check-label"
                          :for="`customCheck${index}`"
                          >&nbsp;</label
                        >
                      </div>
                    </td>
                    <td>
                      <router-link
                        tag="a"
                        to="/apps/ecommerce/order-detail"
                        class="text-body fw-bold"
                        >{{ order.id }}
                      </router-link>
                    </td>
                    <td>
                      {{ order.date }}
                      <small class="text-muted">{{ order.time }}</small>
                    </td>
                    <td>
                      <h5>
                        <span
                          class="badge badge-success-lighten"
                          :class="{
                            'badge-warning-lighten':
                              order.status === 'Awaiting Authorization',
                            'badge-danger-lighten':
                              order.status === 'Payment Failed',
                          }"
                        >
                          <i
                            class="mdi"
                            :class="{
                              'mdi-bitcoin': order.status === 'Paid',
                              'mdi-timer-sand':
                                order.status === 'Awaiting Authorization',
                              'mdi-cancel': order.status === 'Payment Failed',
                            }"
                          ></i>
                          {{ order.status }}
                        </span>
                      </h5>
                    </td>
                    <td>{{ order.total }}</td>
                    <td>{{ order.payment }}</td>
                    <td>
                      <h5>
                        <span
                          class="badge badge-info-lighten"
                          :class="{
                            'badge-warning-lighten':
                              order.orderStatus === 'Processing',
                            'badge-danger-lighten':
                              order.orderStatus === 'Cancelled',
                          }"
                          >{{ order.orderStatus }}</span
                        >
                      </h5>
                    </td>
                    <td>
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-eye"></i>
                      </a>
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-square-edit-outline"></i>
                      </a>
                      <a href="javascript:void(0);" class="action-icon">
                        <i class="mdi mdi-delete"></i>
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";

import { orderData } from "./data";
import Breadcrumb from "@/components/breadcrumb.vue";

export default {
  components: { Breadcrumb, Layout },
  data() {
    return {
      orderData: orderData,
      title: "Orders",
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
          text: "Orders",
          active: true,
        },
      ],
    };
  },
};
</script>
