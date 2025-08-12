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

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import Activity from "@/views/dashboards/projects/activity.vue";
import TasksOverview from "@/views/dashboards/projects/tasks-overview.vue";
import Calendar from "@/views/dashboards/projects/calendar.vue";
import Status from "@/views/dashboards/projects/status.vue";
import Stats from "@/views/dashboards/projects/stats.vue";
import Tasks from "@/views/dashboards/projects/tasks.vue";

export default {
  components: {Tasks, Stats, Status, Calendar, TasksOverview, Activity, Breadcrumb, Layout},
  data(){
    return{
      title: 'Projects',
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
          text: 'Projects',
          active: true,
        },
      ],
    }
  }

}
</script>
