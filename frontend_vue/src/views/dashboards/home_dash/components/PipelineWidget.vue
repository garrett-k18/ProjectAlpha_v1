<template>
  <!--
    Pipeline Widget
    Displays asset pipeline stages by outcome track (FC, REO, DIL, etc.)
    Component path: frontend_vue/src/views/dashboards/home_dash/components/PipelineWidget.vue
    API: GET /api/am/dashboard/pipeline/
  -->
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Asset Pipeline</h4>
      <div class="d-flex align-items-center gap-2">
        <span class="badge bg-primary">{{ activeAssetCount }} Active</span>
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          @click="showFilters = !showFilters"
        >
          <i class="mdi mdi-tune-variant"></i>
          <span v-if="activeFilterCount" class="badge bg-secondary ms-1">{{ activeFilterCount }}</span>
        </button>
      </div>
    </div>
    <div class="card-body">
      <!-- Loading state -->
      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error state -->
      <div v-else-if="error" class="alert alert-danger mb-0">
        <i class="mdi mdi-alert-circle me-2"></i>
        {{ error }}
      </div>

      <!-- Pipeline content -->
      <div v-else>
        <div class="mb-3">
          <div v-if="activeFilterCount" class="d-flex flex-wrap align-items-center gap-2 mb-2">
            <span class="text-muted small">Filters:</span>
            <span
              v-for="(f, idx) in activeFilters"
              :key="`af-${idx}`"
              class="badge bg-soft-primary text-primary"
            >
              {{ f }}
            </span>
            <button type="button" class="btn btn-sm btn-link p-0" @click="clearFilters">Clear</button>
          </div>

          <div v-if="showFilters" class="p-3 bg-light rounded border">
            <b-row class="g-2">
              <b-col cols="12" md="4">
                <label class="form-label mb-1 small text-muted">Trade</label>
                <select v-model="tradeFilter" class="form-select form-select-sm">
                  <option v-for="opt in tradeOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </b-col>
              <b-col cols="12" md="4">
                <label class="form-label mb-1 small text-muted">Partnership</label>
                <select v-model="partnershipFilter" class="form-select form-select-sm">
                  <option v-for="opt in partnershipOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </b-col>
              <b-col cols="12" md="4">
                <label class="form-label mb-1 small text-muted">Asset Manager</label>
                <select v-model="assetManagerFilter" class="form-select form-select-sm">
                  <option v-for="opt in assetManagerOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </b-col>
            </b-row>
          </div>
        </div>

        <!-- Track tabs -->
        <ul class="nav nav-tabs nav-bordered mb-3">
          <li v-for="track in trackOrder" :key="track.key" class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTrack === track.key }"
              href="#"
              @click.prevent="activeTrack = track.key"
            >
              {{ track.label }}
              <span class="badge bg-soft-primary text-primary ms-1">{{ totals[track.key] || 0 }}</span>
            </a>
          </li>
          <!-- Recently Liquidated tab -->
          <li class="nav-item">
            <a 
              class="nav-link" 
              :class="{ active: activeTrack === 'liquidated' }"
              href="#"
              @click.prevent="activeTrack = 'liquidated'"
            >
              <i class="mdi mdi-check-circle-outline me-1"></i>
              Liquidated
              <span class="badge bg-soft-success text-success ms-1">{{ visibleLiquidatedTotal }}</span>
            </a>
          </li>
        </ul>

        <!-- Stage cards for active pipeline tracks -->
        <b-row v-if="activeTrack !== 'liquidated'">
          <b-col 
            v-for="stage in getStagesForTrack(activeTrack)" 
            :key="`${activeTrack}-${stage.task_type}`"
            cols="6" 
            md="4" 
            lg="3"
            xl="2"
            class="mb-3"
          >
            <div 
              class="card border h-100 stage-card cursor-pointer"
              :class="{ 'border-primary': stage.count > 0 }"
              @click="navigateToAssets(activeTrack, stage.task_type)"
            >
              <div class="card-body text-center py-3">
                <h3 class="mb-1" :class="stage.count > 0 ? 'text-primary' : 'text-muted'">
                  {{ stage.count }}
                </h3>
                <div class="small text-muted text-truncate" :title="stage.label">
                  {{ stage.label }}
                </div>
              </div>
            </div>
          </b-col>
        </b-row>

        <!-- Recently Liquidated breakdown -->
        <b-row v-else>
          <b-col 
            v-for="liq in liquidatedBreakdown" 
            :key="liq.key"
            cols="6" 
            md="4" 
            lg="3"
            xl="2"
            class="mb-3"
          >
            <div 
              class="card border h-100 stage-card cursor-pointer"
              :class="{ 'border-success': liq.count > 0 }"
              @click="navigateToLiquidated(liq.key)"
            >
              <div class="card-body text-center py-3">
                <h3 class="mb-1" :class="liq.count > 0 ? 'text-success' : 'text-muted'">
                  {{ liq.count }}
                </h3>
                <div class="small text-muted text-truncate" :title="liq.label">
                  {{ liq.label }}
                </div>
              </div>
            </div>
          </b-col>
        </b-row>

 
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import axios from 'axios';

export interface StageItem {
  stage: string;
  count: number;
  track: string;
  task_type: string;
  order: number;
}

export interface RecentlyLiquidated {
  fc_sale: number;
  reo: number;
  short_sale: number;
  note_sale: number;
  dil: number;
  modification: number;
  total: number;
}

export interface LiquidatedCard {
  key: 'fc_sale' | 'reo' | 'short_sale' | 'note_sale';
  label: string;
  count: number;
}

export interface PipelineData {
  tracks: Record<string, Record<string, number>>;
  summary: StageItem[];
  totals: Record<string, number>;
  active_asset_count: number;
  recently_liquidated: RecentlyLiquidated;
  liquidated_asset_count: number;
}

export default defineComponent({
  name: 'PipelineWidget',

  setup() {
    const loading = ref(true);
    const error = ref<string | null>(null);
    const pipelineData = ref<PipelineData | null>(null);
    const activeTrack = ref('modification');

    const emptyRecentlyLiquidated: RecentlyLiquidated = {
      fc_sale: 0,
      reo: 0,
      short_sale: 0,
      note_sale: 0,
      dil: 0,
      modification: 0,
      total: 0,
    };

    const showFilters = ref(false);
    const tradeFilter = ref('');
    const partnershipFilter = ref('');
    const assetManagerFilter = ref('');

    const tradeOptions = [
      { value: '', label: 'All Trades' },
      { value: 'trade_1', label: 'Trade 1' },
      { value: 'trade_2', label: 'Trade 2' },
    ];

    const partnershipOptions = [
      { value: '', label: 'All Partnerships' },
      { value: 'fund_a', label: 'Fund A' },
      { value: 'jv_1', label: 'JV 1' },
    ];

    const assetManagerOptions = [
      { value: '', label: 'All Asset Managers' },
      { value: 'am_1', label: 'AM 1' },
      { value: 'am_2', label: 'AM 2' },
    ];

    const trackOrder = [
      { key: 'modification', label: 'Modification' },
      { key: 'short_sale', label: 'Short Sale' },
      { key: 'fc', label: 'Foreclosure' },
      { key: 'dil', label: 'DIL' },
      { key: 'reo', label: 'REO Sale' },
      { key: 'note_sale', label: 'Note Sale' },
    ];

    const stageLabels: Record<string, Record<string, string>> = {
      fc: {
        nod_noi: 'NOD/NOI',
        fc_filing: 'FC Filing',
        mediation: 'Mediation',
        judgement: 'Judgement',
        redemption: 'Redemption',
        sale_scheduled: 'Sale Scheduled',
      },
      reo: {
        eviction: 'Eviction',
        trashout: 'Trashout',
        renovation: 'Renovation',
        marketing: 'Marketing',
        under_contract: 'Under Contract',
      },
      dil: {
        pursuing_dil: 'Pursuing DIL',
        owner_contacted: 'Owner Contacted',
        dil_drafted: 'Drafted',
        dil_executed: 'Executed',
      },
      short_sale: {
        list_price_accepted: 'List Price Accepted',
        listed: 'Listed',
        under_contract: 'Under Contract',
      },
      modification: {
        mod_drafted: 'Drafted',
        mod_executed: 'Executed',
        mod_rpl: 'Re-Performing',
        mod_failed: 'Failed',
      },
      note_sale: {
        potential_note_sale: 'Potential',
        out_to_market: 'Out to Market',
        pending_sale: 'Pending Sale',
      },
    };

    const activeAssetCount = computed(() => pipelineData.value?.active_asset_count || 0);
    const liquidatedAssetCount = computed(() => pipelineData.value?.liquidated_asset_count || 0);
    const totals = computed(() => pipelineData.value?.totals || {});
    const recentlyLiquidated = computed<RecentlyLiquidated>(() => pipelineData.value?.recently_liquidated || emptyRecentlyLiquidated);
    
    // Liquidated breakdown for display cards
    const liquidatedBreakdown = computed(() => {
      const liq = recentlyLiquidated.value;
      const cards: LiquidatedCard[] = [
        { key: 'fc_sale', label: 'FC Sale', count: liq.fc_sale },
        { key: 'reo', label: 'REO Sale', count: liq.reo },
        { key: 'short_sale', label: 'Short Sale', count: liq.short_sale },
        { key: 'note_sale', label: 'Note Sale', count: liq.note_sale },
      ];
      return cards;
    });

    const visibleLiquidatedTotal = computed(() => {
      return liquidatedBreakdown.value.reduce((sum: number, item: LiquidatedCard) => sum + item.count, 0);
    });

    const activeFilters = computed(() => {
      const labels: string[] = [];
      const tradeLabel = tradeOptions.find(o => o.value === tradeFilter.value)?.label;
      const partnershipLabel = partnershipOptions.find(o => o.value === partnershipFilter.value)?.label;
      const amLabel = assetManagerOptions.find(o => o.value === assetManagerFilter.value)?.label;

      if (tradeFilter.value && tradeLabel) labels.push(tradeLabel);
      if (partnershipFilter.value && partnershipLabel) labels.push(partnershipLabel);
      if (assetManagerFilter.value && amLabel) labels.push(amLabel);
      return labels;
    });

    const activeFilterCount = computed(() => activeFilters.value.length);

    const clearFilters = () => {
      tradeFilter.value = '';
      partnershipFilter.value = '';
      assetManagerFilter.value = '';
    };

    const topStages = computed(() => {
      if (!pipelineData.value?.summary) return [];
      return [...pipelineData.value.summary]
        .filter(s => s.count > 0)
        .sort((a, b) => b.count - a.count)
        .slice(0, 6);
    });

    const getStagesForTrack = (trackKey: string) => {
      const trackData = pipelineData.value?.tracks[trackKey] || {};
      const labels = stageLabels[trackKey] || {};
      
      return Object.keys(labels).map(taskType => ({
        task_type: taskType,
        label: labels[taskType],
        count: trackData[taskType] || 0,
      }));
    };

    const navigateToAssets = (track: string, taskType: string) => {
      // TODO: Navigate to asset grid filtered by track/stage
      console.log(`Navigate to ${track}/${taskType}`);
    };

    const navigateToLiquidated = (liquidationType: string) => {
      // TODO: Navigate to asset grid filtered by liquidation type
      console.log(`Navigate to liquidated/${liquidationType}`);
    };

    const fetchPipelineData = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await axios.get('/api/am/dashboard/pipeline/');
        pipelineData.value = response.data;
      } catch (err: any) {
        error.value = err.response?.data?.detail || 'Failed to load pipeline data';
        console.error('Pipeline fetch error:', err);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchPipelineData();
    });

    return {
      loading,
      error,
      activeTrack,
      trackOrder,
      activeAssetCount,
      liquidatedAssetCount,
      showFilters,
      tradeFilter,
      partnershipFilter,
      assetManagerFilter,
      tradeOptions,
      partnershipOptions,
      assetManagerOptions,
      activeFilters,
      activeFilterCount,
      clearFilters,
      totals,
      recentlyLiquidated,
      liquidatedBreakdown,
      visibleLiquidatedTotal,
      topStages,
      getStagesForTrack,
      navigateToAssets,
      navigateToLiquidated,
    };
  },
});
</script>

<style scoped>
.stage-card {
  transition: all 0.2s ease-in-out;
}

.stage-card:hover {
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.cursor-pointer {
  cursor: pointer;
}

.bg-soft-primary {
  background-color: rgba(114, 124, 245, 0.18) !important;
}

.bg-soft-success {
  background-color: rgba(10, 179, 156, 0.18) !important;
}

.nav-bordered .nav-link {
  border: 1px solid transparent;
  border-bottom: none;
}

.nav-bordered .nav-link.active {
  border-color: #dee2e6 #dee2e6 #fff;
  background-color: #fff;
}
</style>
