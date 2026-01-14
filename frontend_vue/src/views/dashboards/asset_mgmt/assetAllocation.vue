<template>
  <div class="card widget-flat h-100 flex-grow-1">
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="header-title mb-0">Asset Allocation</h4>
        <div class="dropdown">
          <b-dropdown toggle-class="arrow-none card-drop p-0" variant="link" right>
            <template v-slot:button-content>
              <i class="mdi mdi-dots-vertical text-muted"></i>
            </template>
            <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-download me-1"></i> Export</b-dropdown-item>
            <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-refresh me-1"></i> Refresh</b-dropdown-item>
          </b-dropdown>
        </div>
      </div>

      <div v-if="isLoading" class="d-flex justify-content-center align-items-center flex-grow-1" style="min-height: 300px;">
        <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
      </div>
      <div v-else class="row align-items-center g-0 flex-grow-1">
          <!-- Chart Column -->
          <div class="col-7">
            <apexchart
              height="360"
              type="donut"
              class="apex-charts"
              :series="series"
              :options="chartOptions"
            ></apexchart>
          </div>
          
          <!-- Legend/Stats Column -->
          <div class="col-5">
            <div class="ps-2">
              <div class="mb-3">
                <span class="text-muted text-uppercase small fw-bold" style="letter-spacing: 0.05em;">Active</span>
              </div>
              <div v-for="(label, index) in chartOptions.labels" :key="label" class="mb-4">
              <div class="d-flex align-items-center justify-content-between mb-1">
                <div class="d-flex align-items-center flex-fill text-truncate">
                  <span 
                    class="rounded-circle me-2 flex-shrink-0" 
                    :style="{ backgroundColor: chartOptions.colors[index], width: '8px', height: '8px' }"
                  ></span>
                  <span class="text-dark fw-medium text-truncate" style="font-size: 0.9rem;">{{ label }}</span>
                </div>
                <span class="fw-bold text-dark ms-2" style="font-size: 0.9rem;">{{ series[index] }}</span>
              </div>
              <div class="progress" style="height: 4px; background-color: rgba(0,0,0,0.03);">
                <div 
                  class="progress-bar" 
                  role="progressbar" 
                  :style="{ width: calculatePercentage(series[index]) + '%', backgroundColor: chartOptions.colors[index] }" 
                  :aria-valuenow="calculatePercentage(series[index])" 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                ></div>
              </div>
              <div class="text-end mt-1">
                <span class="text-muted" style="font-size: 0.75rem;">{{ calculatePercentage(series[index]) }}%</span>
              </div>
            </div>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import http from '@/lib/http'

/**
 * AssetAllocationChart
 * 
 * WHAT: Refactored professional donut chart for Asset Allocation.
 * WHY: Provides a high-level portfolio overview with finance-focused aesthetics.
 * HOW: Uses ApexCharts with ProjectAlpha brand colors and custom side-legend with progress bars.
 */
export default defineComponent({
  name: 'AssetAllocationChart',
  data() {
    return {
      isLoading: false,
      series: [0, 0, 0], // NPL, Performing, REO
      totalCount: 0,
      activeTotal: 0,
      liquidatedTotal: 0,
      chartOptions: {
        chart: {
          type: 'donut',
          fontFamily: 'inherit',
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800,
          }
        },
        dataLabels: {
          enabled: false
        },
        legend: {
          show: false // Using custom HTML legend for better professional look
        },
        stroke: {
          width: 2,
          colors: ['#ffffff']
        },
        labels: ['NPL', 'Performing', 'REO'],
        // Brand Colors from _color-palette.scss
        // NPL: Error Red (#C62828), Performing: Success Green (#2E7D32), REO: Slate Teal (#5A8A95), Liquidated: Accent Gold (#D4AF37)
        colors: ['#C62828', '#2E7D32', '#5A8A95'],
        plotOptions: {
          pie: {
            donut: {
              size: '75%',
              labels: {
                show: true,
                name: {
                  show: true,
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#6C757D',
                  offsetY: -5
                },
                value: {
                  show: true,
                  fontSize: '18px',
                  fontWeight: 700,
                  color: '#1B3B5F', // primary-navy
                  offsetY: 5,
                  formatter: (val: string) => val
                },
                total: {
                  show: true,
                  label: 'TOTAL',
                  fontSize: '10px',
                  fontWeight: 600,
                  color: '#95A5A6', // medium-gray
                  formatter: (w: any) => {
                    return w.globals.seriesTotals.reduce((a: number, b: number) => a + b, 0)
                  }
                }
              }
            }
          }
        },
        tooltip: {
          enabled: true,
          y: {
            formatter: (val: number) => `${val} Assets`
          }
        }
      },
    }
  },
  methods: {
    calculatePercentage(value: number): string {
      if (this.totalCount === 0) return '0'
      return ((value / this.totalCount) * 100).toFixed(1)
    },
    async fetchAllocationData() {
      this.isLoading = true
      try {
        const { data } = await http.get('/am/dashboard/stats/')

        this.activeTotal = Number(data.active_assets ?? 0)
        this.liquidatedTotal = Number(data.liquidated_assets ?? 0)
        
        if (data.allocation) {
          const a = data.allocation
          // Order must match labels: ['NPL', 'Performing', 'REO']
          const newSeries = [
            a.NPL || 0,
            a.Performing || 0,
            a.REO || 0
          ]
          this.series = newSeries
          this.totalCount = newSeries.reduce((acc, curr) => acc + curr, 0)
        }
      } catch (error) {
        console.error('[Sales] Failed to load allocation data', error)
      } finally {
        this.isLoading = false
      }
    }
  },
  mounted() {
    this.fetchAllocationData()
  }
})
</script>

<style scoped>
.text-primary-navy {
  color: #1B3B5F;
}
.tiny-text {
  font-size: 0.65rem;
}
.card-header .header-title {
  font-size: 1.1rem;
  letter-spacing: 0.02em;
}
/* Professional progress bar background */
.progress {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
.progress-bar {
  border-radius: 10px;
}
</style>
