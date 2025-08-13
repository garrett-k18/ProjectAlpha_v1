<template>
  <div class="card card-h-100">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title mb-0">Daily Task</h4>
      <div>
        <select class="form-select form-select-sm" aria-label=".form-select-sm example">
          <option selected>Today</option>
          <option value="1">Yesterday</option>
          <option value="2">Tomorrow</option>
        </select>
      </div>
    </div>

    <div class="card-body py-0 mb-3" data-simplebar style="max-height: 304px;">

      <div v-for="(task,index) in taskData" :key="index" class="border rounded p-2 mb-2">
        <ul class="list-inline mb-2">
          <li class="list-inline-item font-16 fw-semibold"><a href="javascript:void(0);"
                                                              class="text-reset">{{ task.title }}</a></li>
          <li class="list-inline-item text-muted"><i class="mdi mdi-circle-small"></i></li>
          <li class="list-inline-item font-13 fw-semibold text-muted">{{ task.time }} ago</li>
        </ul>
        <p class="text-muted mb-0">{{ task.task }}</p>
        <p class="text-muted mb-0"><i class="mdi mdi-account-group me-1"></i> <b>{{ task.people }}</b> People</p>
      </div>

      <div class="text-center">
        <i class="mdi mdi-dots-circle mdi-spin font-20 text-muted"></i>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      taskData: [
        {
          title: 'Landing Page Design',
          time: '2 Hrs',
          task: 'Create a new landing page (Saas Product)',
          people: 5
        },
        {
          title: 'Admin Dashboard',
          time: '3 Hrs',
          task: 'Create a new Admin dashboard',
          people: 2
        },
        {
          title: 'Client Work',
          time: '5 Hrs',
          task: 'Create a new Power Project (Sktech design)',
          people: 2
        },
        {
          title: 'UI/UX Design',
          time: '6 Hrs',
          task: 'Create a new UI Kit in figma',
          people: 3
        },
      ]
    }
  }
}
</script>
