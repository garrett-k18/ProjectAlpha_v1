<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Project Status</h4>
      <div class="float-end">
        <b-dropdown
          toggle-class="arrow-none card-drop p-0"
          variant="black"
          right
        >
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);"
            >Weekly Report</b-dropdown-item
          >
          <b-dropdown-item href="javascript:void(0);"
            >Monthly Report</b-dropdown-item
          >
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <div class="mt-3 mb-4 chartjs-chart" style="height: 204px">
        <Doughnut
          id="project-status-chart"
          :options="chartOptions"
          :data="chartData"
        ></Doughnut>
      </div>

      <b-row class="text-center mt-2 py-2">
        <b-col sm="4">
          <div class="my-2 my-sm-0">
            <i class="mdi mdi-trending-up text-success mt-3 h3"></i>
            <h3 class="fw-normal">
              <span>64%</span>
            </h3>
            <p class="text-muted mb-0">Completed</p>
          </div>
        </b-col>
        <b-col sm="4">
          <div class="my-2 my-sm-0">
            <i class="mdi mdi-trending-down text-primary mt-3 h3"></i>
            <h3 class="fw-normal">
              <span>26%</span>
            </h3>
            <p class="text-muted mb-0">In-progress</p>
          </div>
        </b-col>
        <b-col sm="4">
          <div class="my-2 my-sm-0">
            <i class="mdi mdi-trending-down text-danger mt-3 h3"></i>
            <h3 class="fw-normal">
              <span>10%</span>
            </h3>
            <p class="text-muted mb-0">Behind</p>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
import { Bar, Doughnut } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);
export default {
  components: { Bar, Doughnut },
  data() {
    return {
      chartData: {
        labels: ["Completed", "In-progress", "Behind"],
        datasets: [
          {
            data: [64, 26, 10],
            backgroundColor: ["#0acf97", "#727cf5", "#fa5c7c"],
            borderColor: "transparent",
            borderWidth: "3",
          },
        ],
      },
      chartOptions: {
        maintainAspectRatio: false,
        cutout: 80,
        plugins: {
          cutoutPercentage: 40,
          legend: {
            display: false,
          },
        },
      },
    };
  },
};
</script>
