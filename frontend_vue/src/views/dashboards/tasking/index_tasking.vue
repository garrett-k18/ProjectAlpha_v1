<template>
<Layout>
  <Breadcrumb :title="title" :items="items" />
  <b-row>
    <b-col cols="12">
      <Stats />
    </b-col>
  </b-row>

  <b-row>
    <b-col lg="4">
      <Status />
    </b-col>

    <b-col lg="8">
      <Tasks />
    </b-col>
  </b-row>

  <b-row>
    <b-col cols="12">
    <TasksOverview />
    </b-col>
  </b-row>

  <b-row>
    <b-col xl="5">
      <Activity />
    </b-col>

    <b-col xl="7">
      <Calendar />
    </b-col>
  </b-row>
</Layout>
</template>

<!-- @ts-nocheck -->
<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Activity from "@/views/dashboards/tasking/activity.vue";
import TasksOverview from "@/views/dashboards/tasking/tasks-overview.vue";
import Calendar from "@/views/dashboards/tasking/calendar.vue";
import Status from "@/views/dashboards/tasking/status.vue";
import Stats from "@/views/dashboards/tasking/stats.vue";
import Tasks from "@/views/dashboards/tasking/tasks.vue";

export default {
  components: {Tasks, Stats, Status, Calendar, TasksOverview, Activity, Breadcrumb, Layout},
  data(){
    return{
      title: 'Tasking',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Dashboard',
          href: '/',
        },
        {
          text: 'Tasking',
          active: true,
        },
      ],
    }
  }

}
</script>
