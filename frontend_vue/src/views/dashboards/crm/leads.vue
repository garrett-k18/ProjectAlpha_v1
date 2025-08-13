<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Recent Leads</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="black" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-2">
      <div v-for="(leads,index) of leadsData" :key="leads.name" class="d-flex align-items-start" :class="index !== 0 ? 'mt-3' : ''">
        <img
            class="me-3 rounded-circle"
            :src="`${leads.image}`"
            width="40"
            alt=""
        />
        <div class="w-100 overflow-hidden">
          <span
              class="badge float-end"
              :class="{ 'badge-success-lighten': `${leads.status}` === 'Won lead',
            'badge-danger-lighten': `${leads.status}` === 'Lost lead',
            'badge-warning-lighten': `${leads.status}` === 'Cold lead' }"
          >{{ leads.status }}</span>
          <h5 class="mt-0 mb-1">{{ leads.name }}</h5>
          <span class="font-13">{{ leads.email }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import avatar1 from "@/assets/images/users/avatar-1.jpg"
import avatar2 from "@/assets/images/users/avatar-2.jpg"
import avatar3 from "@/assets/images/users/avatar-3.jpg"
import avatar4 from "@/assets/images/users/avatar-4.jpg"
import avatar5 from "@/assets/images/users/avatar-5.jpg"
import avatar6 from "@/assets/images/users/avatar-6.jpg"

export default {
  data() {
    return {
      leadsData: [
        {
          image: avatar2,
          name: 'Risa Pearson',
          email: 'richard.john@mail.com',
          status: 'Cold lead',
        },
        {
          image: avatar3,
          name: 'Margaret D. Evans',
          email: 'margaret.evans@rhyta.com',
          status: 'Lost lead',
        },
        {
          image: avatar4,
          name: 'Bryan J. Luellen',
          email: 'bryuellen@dayrep.com',
          status: 'Won lead',
        },
        {
          image: avatar5,
          name: 'Kathryn S. Collier',
          email: 'collier@jourrapide.com',
          status: 'Cold lead',
        },
        {
          image: avatar1,
          name: 'Timothy Kauper',
          email: 'thykauper@rhyta.com',
          status: 'Cold lead',
        },
        {
          image: avatar6,
          name: 'Zara Raws',
          email: 'austin@dayrep.com',
          status: 'Won lead',
        },
      ],
    }
  },
}
</script>