<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Project Summary</h4>

      <b-dropdown class="float-end" variant="white"  right toggle-tag="a" toggle-class="arrow-none p-0">
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript: void(0);">Refresh Report</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Export Report</b-dropdown-item>
      </b-dropdown>

    </div>
    <div class="alert alert-warning border-0 rounded-0" role="alert">
      <i class="uil-folder-heart me-1 h4 align-middle"></i> <b>38</b> Total Admin & Client Projects
    </div>

    <div class="card-body pt-1">

      <div v-for="(item,index) in summaryData" :key="index"
           class="d-flex align-items-center border border-light rounded p-2" :class="index!=3 ? 'mb-2':'' ">
        <div class="flex-shrink-0 me-2">
          <i class="mdi widget-icon rounded-circle"
             :class="`${item.icon} bg-${item.color}-lighten text-${item.color}`"></i>
        </div>
        <div class="flex-grow-1">
          <h5 class="fw-semibold my-0">{{ item.title }}</h5>
          <p class="mb-0">{{ item.subtxt }}</p>
        </div>
        <a href="javasript:void(0)" class="text-muted" v-b-tooltip.hover
           title="Info"><i class="mdi mdi-information-outline h4  my-0"></i></a>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      summaryData: [
        {
          title: 'Project Discussion',
          subtxt: '6 Person',
          icon: 'mdi-account-group',
          color: 'primary'
        },
        {
          title: 'In Progress',
          subtxt: '16 Projects',
          icon: 'mdi-progress-pencil',
          color: 'warning'
        },
        {
          title: 'Completed Projects',
          subtxt: '24',
          icon: 'mdi-checkbox-marked-circle-outline',
          color: 'danger'
        },
        {
          title: 'Delivery Projects',
          subtxt: '20',
          icon: 'mdi-send widget-icon',
          color: 'success'
        },
      ]
    }
  }
}
</script>
