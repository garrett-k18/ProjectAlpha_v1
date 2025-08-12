<template>
  <b-col md="6" v-for="(item,index) in statisticsData" :key="index">
    <div class="card">
      <div class="card-body">

        <b-dropdown class="float-end" variant="white" right toggle-tag="a" toggle-class="arrow-none p-0">
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript: void(0);"><i class="uil uil-pen me-1"></i>Edit</b-dropdown-item>
          <b-dropdown-item href="javascript: void(0);" class="text-danger"><i class="uil uil-trash me-1"></i>Remove</b-dropdown-item>
        </b-dropdown>

        <div class="d-flex align-items-center mb-3">
          <div class="flex-shrink-0">
            <div class="avatar-sm">
              <span
                  class="avatar-title rounded" :class="`bg-${item.color}-lighten text-${item.color}`">
                <i class="mdi font-24" :class="item.icon"></i>
              </span>
            </div>
          </div>
          <div class="flex-grow-1 ms-3">
            <a href="javascript:void(0);" class="font-16 fw-bold text-reset">{{ item.title }} <i
                class="mdi mdi-checkbox-marked-circle-outline text-success"></i></a>
            <p class="text-muted mb-0">{{ item.subtxt }}</p>
          </div>
        </div>

        <span class="badge badge-lg bg-light text-reset rounded-pill me-1">{{ item.status }}</span>
        <span class="font-12 fw-semibold text-muted"><i
            class="mdi mdi-clock-time-four me-1"></i>{{ item.hours }} Hours</span>

        <b-row class="mt-2">
          <b-col cols="6" >
            <p class="text-muted fw-semibold mb-1">Tasks</p>
            <h3 class="my-0 text-muted fw-normal">{{ item.tasks }}</h3>
          </b-col>
          <b-col cols="6" class="text-end">
            <p class="text-muted fw-semibold mb-1">Assign to</p>
            <div class="multi-user">
              <a v-for="(img,index) in item.assignees" :key="index" href="javascript:void(0);" class="d-inline-block">
                <img :src="img" class="rounded-circle avatar-xs" alt="friend">
              </a>
            </div>
          </b-col>
        </b-row>

      </div>
    </div>
  </b-col> <!-- end col -->
</template>

<script lang="ts">

import avatar1 from '@/assets/images/users/avatar-1.jpg'
import avatar2 from '@/assets/images/users/avatar-2.jpg'
import avatar3 from '@/assets/images/users/avatar-3.jpg'
import avatar4 from '@/assets/images/users/avatar-4.jpg'
import avatar5 from '@/assets/images/users/avatar-5.jpg'
import avatar6 from '@/assets/images/users/avatar-6.jpg'

export default {
  data() {
    return {
      statisticsData: [
        {
          title: 'Ecommerce App Design',
          subtxt: 'Dashboard, Pages & Auth Pages',
          status: 'Work in Progress',
          hours: 145,
          tasks: 16,
          assignees: [avatar1, avatar2, avatar3],
          icon: 'mdi-shopping-outline',
          color: 'primary'
        },
        {
          title: 'Client Power System',
          subtxt: 'Dashboard, Power System Pages',
          status: 'Work in Progress',
          hours: 260,
          tasks: 24,
          assignees: [avatar4, avatar3],
          icon: 'mdi-account-network',
          color: 'success'
        },
        {
          title: 'Landing Pages Design',
          subtxt: 'Business Landing with Auth Pages',
          status: 'Work in Progress',
          hours: 48,
          tasks: 5,
          assignees: [avatar5, avatar6],
          icon: 'mdi-account-network',
          color: 'info'
        },
        {
          title: 'Business Dashboard Design ',
          subtxt: 'Dashboard, Power System Pages',
          status: 'Work in Progress',
          hours: 24,
          tasks: 8,
          assignees: [avatar5, avatar6,avatar2],
          icon: 'mdi-monitor-dashboard',
          color: 'danger'
        },
      ]
    }
  }
}
</script>
