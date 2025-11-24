<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="!data || data.length === 0" class="text-center py-5 text-muted">
      <i class="uil uil-chart-line" style="font-size: 3rem;"></i>
      <p class="mt-2">No data available</p>
    </div>
    <div v-else>
      <base-apex-chart
        type="area"
        :series="series"
        :options="chartOptions"
        height="300"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseApexChart from '@/components/base-apex-chart.vue'

const props = defineProps<{
  data: any[]
  loading: boolean
}>()

const series = computed(() => [
  {
    name: 'Debits',
    data: props.data.map(item => parseFloat(item.total_debits) || 0)
  },
  {
    name: 'Credits',
    data: props.data.map(item => parseFloat(item.total_credits) || 0)
  }
])

const chartOptions = computed(() => ({
  chart: {
    type: 'area',
    toolbar: { show: false }
  },
  colors: ['#0acf97', '#fa5c7c'],
  stroke: {
    width: 2,
    curve: 'smooth'
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.4,
      opacityTo: 0.1
    }
  },
  xaxis: {
    categories: props.data.map(item => item.month_display || 'Unknown')
  },
  yaxis: {
    labels: {
      formatter: (val: number) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(val)
      }
    }
  },
  dataLabels: {
    enabled: false
  },
  legend: {
    position: 'top',
    horizontalAlign: 'right'
  }
}))
</script>

