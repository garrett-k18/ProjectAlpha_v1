<template>
  <div class="card card-h-100">
    <div class="card-header d-flex justify-content-between align-items-center mt-1">
      <h4 class="header-title">Project Overview</h4>

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

    <div class="card-body pt-0">
      <b-row class="align-items-center">
        <b-col md="6" class="order-2 order-md-1">
          <div v-for="(overview,index) in overviewData" class="d-flex align-items-center " :class="index!=3?'mb-3':''">
            <div class="flex-shrink-0">
              <i class="mdi mdi-checkbox-blank-circle widget-icon rounded-circle"
                 :class="`bg-${overview.color}-lighten text-${overview.color}`"></i>
            </div>
            <div class="flex-grow-1 ms-3">
              <h5 class="fw-semibold mt-0 mb-1">{{ overview.title }}</h5>
              <ul class="list-inline mb-0 text-muted">
                <li class="list-inline-item"><b>{{ overview.projects }}</b> Total Projects</li>
                <li class="list-inline-item"><i class="mdi mdi-circle-small"></i></li>
                <li class="list-inline-item"><b>{{ overview.employees }}</b> Employees</li>
              </ul>
            </div>
          </div>

        </b-col>

        <b-col md="6" class="order-1 order-md-2">
          <div class="mb-3 mb-md-0">
            <BaseApexChart class="apex-charts" :height="326" :series="overviewChart.series" :options="overviewChart.options"/>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">

import BaseApexChart from "@/components/base-apex-chart.vue";

export default {
  components: {BaseApexChart},
  data() {
    return {
      overviewData: [
        {
          title: 'Product Design',
          projects: 26,
          employees: 4,
          color: 'primary'
        },
        {
          title: 'Web Development',
          projects: 30,
          employees: 5,
          color: 'danger'
        },
        {
          title: 'Illustration Design',
          projects: 12,
          employees: 3,
          color: 'success'
        },
        {
          title: 'UI/UX Design',
          projects: 8,
          employees: 4,
          color: 'warning'
        },
      ],
      overviewChart: {
        series: [85, 70, 80, 65],
        options: {
          chart: {
            height: 326,
            type: 'radialBar'
          },
          colors: ['#727cf5', '#ff679b', '#0acf97', '#ffbc00'],
          labels: ['Product Design', 'Web Development', 'Illustration Design', 'UI/UX Design'],
          plotOptions: {
            radialBar: {
              track: {
                margin: 5,
              }
            }
          }
        }
      }
    }
  }
}
</script>
