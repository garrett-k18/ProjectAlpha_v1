<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Task Status</h4>

      <b-dropdown class="float-end" variant="white" right toggle-tag="a" toggle-class="arrow-none p-0">
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript: void(0);">Today</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Yesterday</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Week</b-dropdown-item>
        <b-dropdown-item href="javascript: void(0);">Last Month</b-dropdown-item>
      </b-dropdown>
    </div>

    <div class="card-body pt-2">
      <div v-for="(task,index) in statusData" :key="index" :class="index!=3?'mb-4':''">
        <div class="d-flex align-items-center mb-2">
          <div class="flex-shrink-0">
            <i class="mdi widget-icon" :class="`${task.icon} bg-${task.color}-lighten text-${task.color}`"></i>
          </div>
          <div class="flex-grow-1 ms-2">
            <h5 class="my-0 fw-semibold">{{ task.title }}</h5>
          </div>
          <h5 class="my-0">{{ task.number }}</h5>
        </div>
        <b-progress :max="100" height="6px">
          <b-progress-bar :value="task.progress" :variant="task.color"/>
        </b-progress>
      </div>
    </div>
  </div>
</template>

<script lang="ts">

type VariantType = {
  variant: "primary" | "secondary" | "success" | "danger" | "warning" | "info" | "light" | "dark" | null
}
export default {
  data() {
    return {
      statusData:[
        {
          title:'Running Project',
          number:'145/160',
          color:'primary',
          progress:91,
          icon:'mdi-file-edit'
        },
        {
          title:'Active Clients',
          number:'40/85',
          color:'success',
          progress:47,
          icon:'mdi-account-multiple'
        },
        {
          title:'New Request',
          number:'68%',
          color:'danger',
          progress:68,
          icon:'mdi-account-multiple-plus'
        },
        {
          title:'Happy Clients',
          number:'48/50',
          color:'info',
          progress:90,
          icon:'mdi-emoticon-happy'
        },
      ]
    }
  }
}
</script>
