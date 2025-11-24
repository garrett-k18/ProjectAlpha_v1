<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="!data || data.length === 0" class="text-center py-5 text-muted">
      <i class="uil uil-chart-pie-alt" style="font-size: 3rem;"></i>
      <p class="mt-2">No data available</p>
    </div>
    <div v-else class="chart-container">
      <base-apex-chart
        type="donut"
        :series="series"
        :options="chartOptions"
        height="300"
      />
      <div class="mt-3">
        <div v-for="(item, index) in data" :key="index" class="d-flex justify-content-between align-items-center mb-2">
          <div>
            <span class="badge" :style="{ backgroundColor: colors[index % colors.length] }">
              {{ item.tag_display || 'Untagged' }}
            </span>
          </div>
          <div class="text-end">
            <div class="fw-bold">{{ formatCurrency(item.net_amount) }}</div>
            <small class="text-muted">{{ item.count }} entries</small>
          </div>
        </div>
      </div>
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

const colors = ['#727cf5', '#0acf97', '#fa5c7c', '#ffbc00', '#39afd1', '#6c757d', '#f672a7', '#5b69bc']

const series = computed(() => {
  if (!props.data || props.data.length === 0) return []
  return props.data.map(item => Math.abs(parseFloat(item.net_amount) || 0))
})

const chartOptions = computed(() => ({
  labels: props.data.map(item => item.tag_display || 'Untagged'),
  colors: colors,
  legend: {
    show: false
  },
  plotOptions: {
    pie: {
      donut: {
        size: '70%'
      }
    }
  },
  dataLabels: {
    enabled: false
  }
}))

function formatCurrency(value: any): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(Math.abs(num || 0))
}
</script>

