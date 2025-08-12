<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>

      <b-col md="6" xxl="3" v-for="(client,index) in clientData" :key="index" class="col-md-6 col-xxl-3">
        <div class="card">
          <div class="card-body">

            <b-dropdown class="float-end" variant="white"  right toggle-tag="a" toggle-class="arrow-none p-0">
              <template v-slot:button-content>
                <i class="mdi mdi-dots-horizontal"></i>
              </template>
              <b-dropdown-item href="javascript: void(0);">View Profile</b-dropdown-item>
              <b-dropdown-item href="javascript: void(0);">Project Info</b-dropdown-item>
            </b-dropdown>

            <div class="text-center">
              <img :src="client.img" class="rounded-circle avatar-md img-thumbnail" alt="friend">
              <h4 class="mt-3 my-1"><a href="/pages/profile-2" class="text-reset">{{ client.name }} <i v-if="client.verified"
                  class="mdi mdi-check-decagram text-success"></i></a></h4>
              <p class="mb-0 text-muted"><i class="mdi mdi-email-outline me-1"></i>{{ client.email }}</p>
              <hr class="bg-dark-lighten my-3">
              <h5 class="mt-3 fw-semibold text-muted">Complete Total <b>{{ client.projects }}</b> Project</h5>

              <b-row class="mt-3">
                <b-col cols="4">
                  <a href="javascript:void(0);" class="btn w-100 btn-light" data-bs-toggle="tooltip"
                     data-bs-placement="top" title="Message"><i class="mdi mdi-message-processing-outline"></i></a>
                </b-col>
                <b-col cols="4">
                  <a href="javascript:void(0);" class="btn w-100 btn-light" data-bs-toggle="tooltip"
                     data-bs-placement="top" title="Call"><i class="mdi mdi-phone"></i></a>
                </b-col>
                <b-col cols="4">
                  <a href="javascript:void(0);" class="btn w-100 btn-light" data-bs-toggle="tooltip"
                     data-bs-placement="top" title="Email"><i class="mdi mdi-email-outline"></i></a>
                </b-col>
              </b-row>
            </div>
          </div>
        </div>
      </b-col> <!-- End col -->

    </b-row> <!-- End row -->

    <b-row class="py-4">
      <b-col cols="12" class="text-center">
        <i class="mdi mdi-dots-circle mdi-spin font-24 text-muted"></i>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";

import {clientData} from "@/views/apps/crm/clients/data";

export default {
  components: {Breadcrumb, Layout},
  data() {
    return {
      title: 'Clients List',
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
          text: 'Clients List',
          active: true,
        },
      ],
      clientData
    }
  }
}
</script>