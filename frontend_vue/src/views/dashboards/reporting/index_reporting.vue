<template>
  <Layout>
    <b-row>
      <b-col class="col-12">
        <div class="page-title-box">
          <h4 class="page-title">Reporting Dashboard</h4>
        </div>
      </b-col>
    </b-row>

    <b-row class="g-2">
      <b-col xl="2" lg="12">
        <ReportingSidebar 
          :current-view="currentView"
          @view-change="handleViewChange"
          @filters-change="handleFiltersChange"
          @reset-filters="handleResetFilters"
          @open-settings="showSettingsModal = true"
        />
      </b-col>

      <b-col xl="10" lg="12">
        <ReportHeader 
          :summary="reportSummary"
          :loading="loadingSummary"
        />

        <div class="mt-2">
          <component 
            :is="currentReportComponent" 
            :chart-data="chartData"
            :grid-data="gridData"
            :loading-chart="loadingChart"
            :loading-grid="loadingGrid"
            @drill-down="handleDrillDown"
          />
        </div>
      </b-col>
    </b-row>

    <DrillDownModal
      v-model="showDrillDownModal"
      :drill-down-type="drillDownType"
      :drill-down-data="drillDownData"
      @close="closeDrillDown"
    />

    <BModal
      v-model="showSettingsModal"
      title="Dashboard Settings"
      size="lg"
      centered
      hide-footer
    >
      <div class="py-3">
        <p class="text-muted">Dashboard settings and saved reports will be configured here.</p>
        <ul class="list-unstyled">
          <li class="mb-2">Save current filter configuration</li>
          <li class="mb-2">Export templates</li>
          <li class="mb-2">Scheduled reports</li>
          <li class="mb-2">Default view preferences</li>
        </ul>
      </div>
      <div class="d-flex justify-content-end gap-2">
        <button class="btn btn-primary" @click="showSettingsModal = false">Close</button>
      </div>
    </BModal>
  </Layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import Layout from "@/components/layouts/layout.vue"
import { BModal } from 'bootstrap-vue-next'
import ReportingSidebar from './components/ReportingSidebar.vue'
import ReportHeader from './components/ReportHeader.vue'
import DrillDownModal from './components/DrillDownModal.vue'
import ByTradeReport from './views/ByTradeReport.vue'
import ByStatusReport from './views/ByStatusReport.vue'
import ByFundReport from './views/ByFundReport.vue'
import ByEntityReport from './views/ByEntityReport.vue'
import OverviewReport from './views/OverviewReport.vue'
import GeographicReport from './views/GeographicReport.vue'
import CollateralReport from './views/CollateralReport.vue'
import TimeSeriesReport from './views/TimeSeriesReport.vue'
import { useReportingStore } from '@/stores/reporting'

export default defineComponent({
  name: 'ReportingDashboard',
  components: {
    Layout,
    BModal,
    ReportingSidebar,
    ReportHeader,
    DrillDownModal,
    ByTradeReport,
    ByStatusReport,
    ByFundReport,
    ByEntityReport,
    OverviewReport,
    GeographicReport,
    CollateralReport,
    TimeSeriesReport,
  },
  setup() {
    const reportingStore = useReportingStore()
    const {
      currentView,
      reportSummary,
      loadingSummary,
      chartData,
      loadingChart,
      gridData,
      loadingGrid,
    } = storeToRefs(reportingStore)

    const showDrillDownModal = ref<boolean>(false)
    const drillDownType = ref<string>('')
    const drillDownData = ref<any>(null)
    const showSettingsModal = ref<boolean>(false)

    const currentReportComponent = computed(() => {
      const viewMap: Record<string, any> = {
        'overview': OverviewReport,
        'by-trade': ByTradeReport,
        'by-status': ByStatusReport,
        'by-fund': ByFundReport,
        'by-entity': ByEntityReport,
        'geographic': GeographicReport,
        'collateral': CollateralReport,
        'timeseries': TimeSeriesReport,
      }
      return viewMap[currentView.value] || OverviewReport
    })

    function handleViewChange(viewName: string): void {
      reportingStore.setView(viewName)
    }

    function handleFiltersChange(): void {
      refreshData()
    }

    function handleResetFilters(): void {
      reportingStore.resetFilters()
      refreshData()
    }

    function handleDrillDown(payload: { type: string; data: any }): void {
      drillDownType.value = payload.type
      drillDownData.value = payload.data
      showDrillDownModal.value = true
    }

    function closeDrillDown(): void {
      showDrillDownModal.value = false
      drillDownType.value = ''
      drillDownData.value = null
    }

    function handleExport(): void {
      console.log('[Reporting] Export requested for view:', currentView.value)
      alert('Export functionality coming soon!')
    }

    async function refreshData(): Promise<void> {
      await Promise.all([
        reportingStore.fetchReportSummary(),
        reportingStore.fetchChartData(),
        reportingStore.fetchGridData(),
      ])
    }

    onMounted(async () => {
      await reportingStore.refreshAllOptions()
      await refreshData()
    })

    watch(currentView, async () => {
      await refreshData()
    })

    return {
      currentView,
      reportSummary,
      loadingSummary,
      chartData,
      loadingChart,
      gridData,
      loadingGrid,
      showDrillDownModal,
      drillDownType,
      drillDownData,
      showSettingsModal,
      currentReportComponent,
      handleViewChange,
      handleFiltersChange,
      handleResetFilters,
      handleDrillDown,
      closeDrillDown,
      handleExport,
    }
  },
})
</script>

<style scoped>
@media (min-width: 1200px) {
  .col-xl-3 {
    position: sticky;
    top: 70px;
    max-height: calc(100vh - 90px);
    overflow-y: auto;
  }
}
</style>
