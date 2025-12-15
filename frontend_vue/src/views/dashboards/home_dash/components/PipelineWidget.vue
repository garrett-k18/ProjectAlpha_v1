<template>
  <!--
    Pipeline Widget
    Displays asset pipeline stages by outcome track (FC, REO, DIL, etc.)
    Component path: frontend_vue/src/views/dashboards/home_dash/components/PipelineWidget.vue
    API: GET /api/am/dashboard/pipeline/
  -->
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">
        <i class="mdi mdi-chart-timeline-variant me-2"></i>
        Asset Pipeline
      </h5>
      <div>
        <span class="badge bg-primary me-2">{{ activeAssetCount }} Active</span>
        <span class="badge bg-success">{{ liquidatedAssetCount }} Liquidated</span>
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

        <!-- Summary row - top stages across all tracks -->
        <div v-if="activeTrack !== 'liquidated'" class="mt-3 pt-3 border-top">
          <h6 class="text-muted mb-2">
            <i class="mdi mdi-trending-up me-1"></i>
            Top Active Stages
          </h6>
          <div class="d-flex flex-wrap gap-2">
            <span 
              v-for="item in topStages" 
              :key="`${item.track}-${item.task_type}`"
              class="badge bg-soft-primary text-primary px-3 py-2 cursor-pointer"
              @click="navigateToAssets(item.track, item.task_type)"
            >
              {{ item.stage }}: {{ item.count }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import axios from 'axios';

interface StageItem {
  stage: string;
  count: number;
  track: string;
  task_type: string;
  order: number;
}

interface RecentlyLiquidated {
  fc_sale: number;
  reo: number;
  short_sale: number;
  note_sale: number;
  dil: number;
  modification: number;
  total: number;
}

interface PipelineData {
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
    const activeTrack = ref('fc');

    const trackOrder = [
      { key: 'fc', label: 'Foreclosure' },
      { key: 'reo', label: 'REO' },
      { key: 'dil', label: 'DIL' },
      { key: 'short_sale', label: 'Short Sale' },
      { key: 'modification', label: 'Modification' },
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
    const recentlyLiquidated = computed(() => pipelineData.value?.recently_liquidated || { total: 0 });
    
    // Liquidated breakdown for display cards
    const liquidatedBreakdown = computed(() => {
      const liq = pipelineData.value?.recently_liquidated || {};
      return [
        { key: 'fc_sale', label: 'FC Sale', count: liq.fc_sale || 0 },
        { key: 'reo', label: 'REO Sale', count: liq.reo || 0 },
        { key: 'short_sale', label: 'Short Sale', count: liq.short_sale || 0 },
        { key: 'note_sale', label: 'Note Sale', count: liq.note_sale || 0 },
      ];
    });

    const visibleLiquidatedTotal = computed(() => {
      return liquidatedBreakdown.value.reduce((sum, item) => sum + (item.count || 0), 0);
    });

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
