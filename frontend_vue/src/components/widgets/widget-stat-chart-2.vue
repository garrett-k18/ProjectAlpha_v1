<template>
  <div class="card">
    <div class="card-body">

      <b-dropdown class="float-end" toggle-class="arrow-none card-drop p-0" variant="black" right>
        <template v-slot:button-content>
          <i class="mdi mdi-dots-horizontal"></i>
        </template>
        <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-cached me-1"></i>Refresh</b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-circle-edit-outline me-1"></i>Edit
        </b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);" class="text-danger"><i class="mdi mdi-delete-outline me-1"></i>Remove
        </b-dropdown-item>
      </b-dropdown>

      <div class="d-flex">
        <div class="flex-shrink-0">
          <div class="avatar-sm rounded">
            <span class="avatar-title bg-primary-lighten h3 my-0 text-primary rounded">
              <i :class="`mdi ${icon}`"></i>
            </span>
          </div>
        </div>
        <div class="flex-grow-1 ms-3">
          <h4 class="mt-0 mb-1 font-20">${{ amount }}</h4>
          <p class="mb-0 text-muted"><i :class="`mdi ${growthIcon} text-success`"></i> {{ growth }}% This Week</p>
        </div>
      </div>

      <b-row class="align-items-end justify-content-between mt-3">
        <b-col sm="6">
          <h4 class="mt-0 text-muted fw-semibold mb-1">Rate</h4>
          <p class="text-muted mb-0">{{ rate }}</p>
        </b-col>

        <b-col sm="5">
          <div class="text-end">
            <div id="currency-btc-chart" data-colors="#727cf5"></div>
            <apexchart :type="`${chartType}`" height="60" :series="series" :options="options"></apexchart>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script lang="ts">
/**
 * A stat show case widget to show progress through chart visulization
 * 1. widget 'icon' represents related icon in widget.
 * 2. widget 'amount' property specify the value of profit or sales etc.
 * 3. widget 'growth' property specify the growth percentage of profit or sales etc.
 * 4. widget 'growthIcon' represents the up-going or down-going icon based on growth.
 * 5. widget rate specify using the 'rate' input property. Rate value consider on amount.
 * 6. Widget chart series data specify using the 'chartData' input property.
 * 7. Using 'chartType' property user specify the chart type such as line, bar.
 * 8. Widget chartColor specify using the 'chartColor' input property.
 */
export default {
  props: {
    icon: {
      type: String,
      default: '',
    },
    amount: {
      type: String,
      default: '',
    },
    growth: {
      type: Number,
      default: '',
    },
    growthIcon: {
      type: String,
      default: '',
    },
    rate: {
      type: String,
      default: '',
    },
    chartData: {
      type: Array,
      required: true,
    },
    chartType: {
      type: String,
      default: 'bar',
    },
    chartColor: {
      type: String,
      default: '#727cf5',
    },
  },
  data() {
    return {
      options: {
        chart: {
          sparkline: {
            enabled: true,
          },
        },
        grid: {
          padding: {
            top: 10,
          },
        },
        plotOptions: {
          bar: {
            columnWidth: '60%',
          },
        },
        xaxis: {
          crosshairs: {
            width: 1,
          },
        },
        tooltip: {
          fixed: {
            enabled: false,
          },
          x: {
            show: false,
          },
          y: {
            title: {
              formatter: (seriesName) => {
                return ''
              },
            },
          },
          marker: {
            show: false,
          },
        },
        stroke: {
          width: 2,
          curve: 'smooth',
        },
        colors: [this.chartColor],
      },
      series: [
        {
          data: this.chartData,
        },
      ],
    }
  }
}
</script>
