<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="!data || data.length === 0" class="text-center py-5 text-muted">
      <i class="uil uil-chart-bar" style="font-size: 3rem;"></i>
      <p class="mt-2">No data available</p>
    </div>
    <div v-else>
      <base-apex-chart
        type="bar"
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

const series = computed(() => [{
  name: 'Net Amount',
  data: props.data.map(item => parseFloat(item.net_amount) || 0)
}])

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      distributed: true
    }
  },
  colors: ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00', '#39afd1', '#6c757d', '#f672a7', '#5b69bc'],
  dataLabels: {
    enabled: false
  },
  xaxis: {
    categories: props.data.map(item => item.bucket_display || 'Unbucketed'),
    labels: {
      formatter: (val: number) => {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Math.abs(val))
      }
    }
  },
  legend: {
    show: false
  }
}))
</script>

