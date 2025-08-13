<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Campaigns</h4>
      <div class="dropdown float-end">
        <b-dropdown
            toggle-class="arrow-none card-drop p-0"
            variant="black"
            right
        >
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Today</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);"
          >Yesterday
          </b-dropdown-item
          >
          <b-dropdown-item href="javascript:void(0);"
          >Last Week
          </b-dropdown-item
          >
          <b-dropdown-item href="javascript:void(0);"
          >Last Month
          </b-dropdown-item
          >
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <apexchart
          type="radialBar"
          height="314"
          :series="series"
          :options="chartOptions"
      ></apexchart>

      <b-row class="text-center mt-3">
        <b-col sm="4">
          <i
              class="mdi mdi-send widget-icon rounded-circle bg-warning-lighten text-warning"
          ></i>
          <h3 class="fw-normal mt-3">
            <span>6,510</span>
          </h3>
          <p class="text-muted mb-0 mb-2">
            <i class="mdi mdi-checkbox-blank-circle text-warning"></i> Total
            Sent
          </p>
        </b-col>
        <b-col sm="4">
          <i
              class="mdi mdi-flag-variant widget-icon rounded-circle bg-primary-lighten text-primary"
          ></i>
          <h3 class="fw-normal mt-3">
            <span>3,487</span>
          </h3>
          <p class="text-muted mb-0 mb-2">
            <i class="mdi mdi-checkbox-blank-circle text-primary"></i> Reached
          </p>
        </b-col>
        <b-col sm="4">
          <i
              class="mdi mdi-email-open widget-icon rounded-circle bg-success-lighten text-success"
          ></i>
          <h3 class="fw-normal mt-3">
            <span>1,568</span>
          </h3>
          <p class="text-muted mb-0 mb-2">
            <i class="mdi mdi-checkbox-blank-circle text-success"></i> Opened
          </p>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      series: [86, 36, 50],
      chartOptions: {
        chart: {
          type: 'radialBar',
          events: {},
        },
        labels: ["Total Sent", "Reached", "Opened"],
        colors: ["#ffbc00", "#727cf5", "#0acf97"],
        plotOptions: {
          radialBar: {
            track: {
              margin: 8,
            },
          },
        },
      },
    };
  },
};
</script>
