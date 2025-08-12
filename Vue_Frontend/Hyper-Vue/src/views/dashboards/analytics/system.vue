<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Sessions by Operating System</h4>
      <div class="float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" :variant="null" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Refresh Report</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Export Report</b-dropdown-item>
        </b-dropdown>
      </div>
    </div>

    <div class="card-body pt-0">
      <apexchart
          height="304"
          type="radialBar"
          class="apex-charts mt-0"
          :series="series"
          :options="chartOptions"
      ></apexchart>

      <b-row class="text-center mt-2">
        <b-col cols="6">
          <h4 class="font-weight-normal">
            <span>6,510</span>
          </h4>
          <p class="text-muted mb-0">Online System</p>
        </b-col>
        <b-col cols="6">
          <h4 class="font-weight-normal">
            <span>2,031</span>
          </h4>
          <p class="text-muted mb-0">Offline System</p>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      chartOptions: {
        chart: {
          type: 'radialBar',
          events: {},
        },
        labels: ['Windows', 'Macintosh', 'Linux', 'Android'],
        colors: ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00'],
        plotOptions: {
          radialBar: {
            dataLabels: {
              name: {
                fontSize: '22px',
              },
              value: {
                fontSize: '16px',
              },
              total: {
                show: true,
                label: 'OS',
                formatter: function () {
                  return 8541
                },
              },
            },
          },
        },
      },
      series: [44, 55, 67, 83],
    }
  },
}
</script>