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
        <button
          type="button"
          class="btn btn-sm btn-outline-secondary"
          @click="showFilters = !showFilters"
        >
          <i class="mdi mdi-tune-variant"></i>
          <span 
            v-if="activeFilterCount" 
            class="badge text-white border-0 ms-1"
            :style="getFilterBadgeStyle()"
          >
            {{ activeFilterCount }}
          </span>
        </button>
      </div>
    </div>
    <div class="card-body">
      <!-- Loading state -->
      <div v-if="loading" class="text-center py-4">
        <div 
          class="spinner-border" 
          role="status"
          :style="getSpinnerStyle()"
        >
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
        <!-- Stage Overview (default view) -->
        <div v-if="!selectedStage">
          <div class="mb-3">
          <div v-if="activeFilterCount" class="d-flex flex-wrap align-items-center gap-2 mb-2">
            <span class="text-muted small">Filters:</span>
            <span
              v-for="(f, idx) in activeFilters"
              :key="`af-${idx}`"
              class="badge text-white border-0"
              :style="getFilterBadgeStyle()"
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
              <span 
                class="badge text-white border-0 ms-1"
                :style="getTrackBadgeStyle(track.key)"
              >
                {{ totals[track.key] || 0 }}
              </span>
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
              <span 
                class="badge text-white border-0 ms-1"
                :style="getLiquidatedBadgeStyle()"
              >
                {{ visibleLiquidatedTotal }}
              </span>
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
              :style="stage.count > 0 ? getStageCardBorderStyle(activeTrack) : {}"
              @click="navigateToAssets(activeTrack, stage.task_type)"
            >
              <div class="card-body text-center py-3">
                <h3 
                  class="mb-1" 
                  :style="stage.count > 0 ? getStageCountStyle(activeTrack) : {}"
                  :class="stage.count > 0 ? '' : 'text-muted'"
                >
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
              :style="liq.count > 0 ? getLiquidatedCardBorderStyle() : {}"
              @click="navigateToLiquidated(liq.key)"
            >
              <div class="card-body text-center py-3">
                <h3 
                  class="mb-1" 
                  :style="liq.count > 0 ? getLiquidatedCountStyle() : {}"
                  :class="liq.count > 0 ? '' : 'text-muted'"
                >
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

        <!-- Asset List View for Selected Stage -->
        <div v-else class="stage-assets-view">
          <!-- Header with breadcrumb navigation -->
          <div class="d-flex align-items-center justify-content-between mb-3 pb-2 border-bottom">
            <h5 class="mb-0 d-flex align-items-center">
              <span 
                class="text-muted breadcrumb-link" 
                @click="goBack"
                role="button"
                tabindex="0"
                @keydown.enter="goBack"
                @keydown.space.prevent="goBack"
              >
                {{ getTrackFullName(activeTrack) }}
              </span>
              <i class="mdi mdi-chevron-right mx-2 text-muted" style="font-size: 0.9em;"></i>
              <span>{{ selectedStage.label }}</span>
            </h5>
            <div class="text-muted small">
              {{ stageAssets.length }} assets
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="assetsLoading" class="text-center py-5">
            <div class="spinner-border" role="status" :style="getSpinnerStyle()">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted mt-2">Loading assets...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="assetsError" class="alert alert-danger">
            <i class="mdi mdi-alert-circle me-2"></i>
            {{ assetsError }}
          </div>

          <!-- Assets List -->
          <div v-else-if="stageAssets.length" class="assets-list">
            <div 
              v-for="asset in stageAssets" 
              :key="asset.id"
              class="asset-card"
              :style="`border-left: 4px solid ${getTagColor(getTrackTagColor(activeTrack))}`"
              @click="$emit('open-asset', { id: asset.asset_hub_id, row: asset, addr: asset.street_address })"
            >
              <div class="asset-card-header">
                <div class="asset-info">
                  <div class="asset-id-line">
                    <span class="asset-id">{{ asset.servicer_id || 'N/A' }}</span>
                    <span v-if="asset.servicer_id && asset.street_address" class="mx-1">-</span>
                    <span class="asset-address">
                      <i class="mdi mdi-map-marker-outline me-1"></i>
                      {{ asset.street_address || 'No address' }}
                      <span v-if="asset.city || asset.state">
                        , {{ [asset.city, asset.state].filter(Boolean).join(', ') }}
                      </span>
                    </span>
                  </div>
                  <div class="asset-trade-line">
                    <i class="mdi mdi-briefcase-outline me-1"></i>
                    <span>{{ asset.trade_name || 'No Trade' }}</span>
                  </div>
                </div>
                <div class="asset-actions">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click.stop="$emit('open-asset', { id: asset.asset_hub_id, row: asset, addr: asset.street_address })"
                    title="View Asset Details"
                  >
                    <i class="mdi mdi-eye"></i>
                  </button>
                </div>
              </div>
              
              <div class="asset-card-body">
                <div class="asset-meta-grid">
                  <div class="meta-item">
                    <span class="meta-label">Status:</span>
                    <span 
                      class="badge text-white border-0"
                      :style="`background-color: ${getTagColor(getTrackTagColor(activeTrack))};`"
                    >
                      {{ selectedStage.label }}
                    </span>
                  </div>
                  <div v-if="asset.latest_uw_value" class="meta-item">
                    <span class="meta-label">Value:</span>
                    <span class="meta-value">${{ formatCurrency(asset.latest_uw_value) }}</span>
                  </div>
                  <div v-if="asset.purchase_cost" class="meta-item">
                    <span class="meta-label">Purchase:</span>
                    <span class="meta-value">${{ formatCurrency(asset.purchase_cost) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="text-center py-5 bg-light rounded border">
            <i class="mdi mdi-package-variant text-muted" style="font-size: 3rem;"></i>
            <p class="text-muted mt-2 mb-0">No assets found in this stage.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import http from '@/lib/http'
import { getTagColor, TAG_COLORS } from '@/GlobalStandardizations/colors';
import { ASSET_PIPELINE_TRACK_COLORS, ASSET_MASTER_STATUS_COLORS } from '@/GlobalStandardizations/badges';

type TagColorName = keyof typeof TAG_COLORS;

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

    // Asset list view state - for displaying assets in a selected stage
    const selectedStage = ref<{ track: string; taskType: string; label: string } | null>(null);
    const stageAssets = ref<any[]>([]);
    const assetsLoading = ref(false);
    const assetsError = ref<string | null>(null);
    const assetsPagination = ref<{ count: number; next: string | null; previous: string | null }>({
      count: 0,
      next: null,
      previous: null
    });

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

    const fetchStageAssets = async (track: string, stage: string, stageLabel: string) => {
      assetsLoading.value = true;
      assetsError.value = null;
      stageAssets.value = [];

      try {
        // Use the existing asset inventory endpoint with filters
        const response = await http.get('/am/assets/', {
          params: {
            active_tracks: track,
            page_size: 50,
          }
        });

        // Filter assets by task type on the frontend using active_tasks field
        // active_tasks contains strings like "FC: Judgement, DIL: Owner contacted"
        const allAssets = response.data.results || [];
        stageAssets.value = allAssets.filter((asset: any) => {
          const activeTasks = asset.active_tasks || '';
          return activeTasks.toLowerCase().includes(String(stageLabel).toLowerCase());
        });

        assetsPagination.value = {
          count: stageAssets.value.length,
          next: null,
          previous: null,
        };
      } catch (err: any) {
        assetsError.value = err.response?.data?.detail || 'Failed to load assets for this stage';
        console.error('Assets fetch error:', err);
      } finally {
        assetsLoading.value = false;
      }
    };

    const navigateToAssets = async (track: string, taskType: string) => {
      const trackLabel = stageLabels[track]?.[taskType] || taskType;
      selectedStage.value = { track, taskType, label: trackLabel };
      await fetchStageAssets(track, taskType, trackLabel);
    };

    const goBack = () => {
      selectedStage.value = null;
      stageAssets.value = [];
    };

    const navigateToLiquidated = (liquidationType: string) => {
      // TODO: Navigate to asset grid filtered by liquidation type
      console.log(`Navigate to liquidated/${liquidationType}`);
    };

    /**
     * WHAT: Get badge style for "Active" count badge
     * WHY: Use project palette color for active status
     * HOW: Use military-green from ASSET_MASTER_STATUS_COLORS
     */
    const getActiveBadgeStyle = (): string => {
      const color = getTagColor(ASSET_MASTER_STATUS_COLORS['ACTIVE']);
      return `background-color: ${color};`;
    };

    /**
     * WHAT: Get badge style for filter count badges
     * WHY: Use consistent tag color for filter badges
     * HOW: Use navy-blue as a neutral tag color
     */
    const getFilterBadgeStyle = (): string => {
      const color = getTagColor('navy-blue');
      return `background-color: ${color};`;
    };

    /**
     * WHAT: Get badge style for track tab badges
     * WHY: Use track-specific colors from ASSET_PIPELINE_TRACK_COLORS
     * HOW: Map track key to color from categoryColors.ts
     */
    const getTrackBadgeStyle = (trackKey: string): string => {
      const trackLabelMap: Record<string, string> = {
        'modification': 'Modification',
        'short_sale': 'Short Sale',
        'fc': 'FC',
        'dil': 'DIL',
        'reo': 'REO Sale',
        'note_sale': 'Note Sale',
      };
      const label = trackLabelMap[trackKey] || trackKey;
      const tagColor = ASSET_PIPELINE_TRACK_COLORS[label] || 'navy-blue';
      const color = getTagColor(tagColor);
      return `background-color: ${color};`;
    };

    /**
     * WHAT: Get badge style for liquidated tab badge
     * WHY: Use warm-yellow from ASSET_MASTER_STATUS_COLORS
     * HOW: Use LIQUIDATED color assignment
     */
    const getLiquidatedBadgeStyle = (): string => {
      const color = getTagColor(ASSET_MASTER_STATUS_COLORS['LIQUIDATED']);
      return `background-color: ${color};`;
    };

    /**
     * WHAT: Get border style for stage cards with counts
     * WHY: Use track-specific colors for card borders
     * HOW: Map track to color and apply as border-color
     */
    const getStageCardBorderStyle = (trackKey: string): string => {
      const trackLabelMap: Record<string, string> = {
        'modification': 'Modification',
        'short_sale': 'Short Sale',
        'fc': 'FC',
        'dil': 'DIL',
        'reo': 'REO Sale',
        'note_sale': 'Note Sale',
      };
      const label = trackLabelMap[trackKey] || trackKey;
      const tagColor = ASSET_PIPELINE_TRACK_COLORS[label] || 'navy-blue';
      const color = getTagColor(tagColor);
      return `border-color: ${color} !important; border-width: 2px;`;
    };

    /**
     * WHAT: Get text color style for stage count numbers
     * WHY: Use track-specific colors for count text
     * HOW: Map track to color and apply as color
     */
    const getStageCountStyle = (trackKey: string): string => {
      const trackLabelMap: Record<string, string> = {
        'modification': 'Modification',
        'short_sale': 'Short Sale',
        'fc': 'FC',
        'dil': 'DIL',
        'reo': 'REO Sale',
        'note_sale': 'Note Sale',
      };
      const label = trackLabelMap[trackKey] || trackKey;
      const tagColor = ASSET_PIPELINE_TRACK_COLORS[label] || 'navy-blue';
      const color = getTagColor(tagColor);
      return `color: ${color};`;
    };

    /**
     * WHAT: Get border style for liquidated cards with counts
     * WHY: Use warm-yellow for liquidated status
     * HOW: Use LIQUIDATED color assignment
     */
    const getLiquidatedCardBorderStyle = (): string => {
      const color = getTagColor(ASSET_MASTER_STATUS_COLORS['LIQUIDATED']);
      return `border-color: ${color} !important; border-width: 2px;`;
    };

    /**
     * WHAT: Get text color style for liquidated count numbers
     * WHY: Use warm-yellow for liquidated status
     * HOW: Use LIQUIDATED color assignment
     */
    const getLiquidatedCountStyle = (): string => {
      const color = getTagColor(ASSET_MASTER_STATUS_COLORS['LIQUIDATED']);
      return `color: ${color};`;
    };

    /**
     * WHAT: Get spinner color style
     * WHY: Use project primary navy color for loading spinner
     * HOW: Use primary navy from color palette
     */
    const getSpinnerStyle = (): string => {
      const color = getTagColor('navy-blue');
      return `color: ${color};`;
    };

    /**
     * WHAT: Get tag color for a track
     * WHY: Use track-specific colors for asset cards
     * HOW: Map track key to ASSET_PIPELINE_TRACK_COLORS
     */
    const getTrackTagColor = (trackKey: string): TagColorName => {
      const trackLabelMap: Record<string, string> = {
        'modification': 'Modification',
        'short_sale': 'Short Sale',
        'fc': 'FC',
        'dil': 'DIL',
        'reo': 'REO',
        'note_sale': 'Note Sale',
      };
      const label = trackLabelMap[trackKey] || trackKey;
      return ASSET_PIPELINE_TRACK_COLORS[label] || 'navy-blue';
    };

    /**
     * WHAT: Get full display name for track abbreviation
     * WHY: Spell out abbreviations like "FC" -> "Foreclosure", "DIL" -> "Deed-in Lieu"
     * HOW: Map track keys to their full names
     */
    const getTrackFullName = (trackKey: string): string => {
      const trackNameMap: Record<string, string> = {
        'modification': 'Modification',
        'short_sale': 'Short Sale',
        'fc': 'Foreclosure',
        'dil': 'Deed-in Lieu',
        'reo': 'REO Sale',
        'note_sale': 'Note Sale',
      };
      return trackNameMap[trackKey] || trackKey;
    };

    /**
     * WHAT: Format currency values
     * WHY: Display monetary values in a readable format
     * HOW: Use toLocaleString with appropriate options
     */
    const formatCurrency = (value: number | string | null): string => {
      if (value == null) return '0';
      const num = typeof value === 'string' ? parseFloat(value) : value;
      if (isNaN(num)) return '0';
      return num.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    };

    const fetchPipelineData = async () => {
      loading.value = true;
      error.value = null;
      try {
        const response = await http.get('/am/dashboard/pipeline/');
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
      selectedStage,
      stageAssets,
      assetsLoading,
      assetsError,
      assetsPagination,
      goBack,
      getActiveBadgeStyle,
      getFilterBadgeStyle,
      getTrackBadgeStyle,
      getLiquidatedBadgeStyle,
      getStageCardBorderStyle,
      getStageCountStyle,
      getLiquidatedCardBorderStyle,
      getLiquidatedCountStyle,
      getSpinnerStyle,
      getTrackTagColor,
      formatCurrency,
      getTagColor,
      getTrackFullName,
    };
  },
  emits: ['open-asset'],
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

.nav-bordered .nav-link {
  border: 1px solid transparent;
  border-bottom: none;
}

/* WHAT: Active tab styling with gold underline
 * WHY: Keep the gold accent color for active tab indicator
 * HOW: Use project accent gold color for bottom border
 */
.nav-bordered .nav-link.active {
  border-color: #dee2e6 #dee2e6 #D4AF37; /* Gold underline - accent color */
  background-color: #FDFBF7; /* Keep beige background for active tab */
  color: #1B3B5F; /* Use primary navy for active tab text */
  font-weight: 600;
}

/* Asset List View Styles */
.stage-assets-view {
  max-height: 600px;
  overflow-y: auto;
  padding-right: 1rem; /* Add padding between content and scrollbar */
}

/* Custom scrollbar styling - subtle and light */
.stage-assets-view::-webkit-scrollbar {
  width: 8px;
}

.stage-assets-view::-webkit-scrollbar-track {
  background: #F1F5F9; /* Light gray track */
  border-radius: 4px;
}

.stage-assets-view::-webkit-scrollbar-thumb {
  background: #CBD5E1; /* Subtle gray thumb */
  border-radius: 4px;
  transition: background 0.2s ease;
}

.stage-assets-view::-webkit-scrollbar-thumb:hover {
  background: #94A3B8; /* Slightly darker on hover */
}

/* Firefox scrollbar styling */
.stage-assets-view {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E1 #F1F5F9;
}

.assets-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-right: 0.5rem; /* Additional padding for content */
}

.asset-card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-left-width: 4px; /* Will be colored via inline style */
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.asset-card:hover {
  background: #F8F9FA;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.asset-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.asset-info {
  flex: 1;
  min-width: 0; /* Enable text truncation if needed */
}

.asset-id-line {
  font-size: 1rem;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  line-height: 1.4;
}

.asset-id {
  font-weight: 600;
  color: #1E293B; /* Slate 800 */
  margin-right: 0.5rem;
  letter-spacing: -0.025em;
  font-size: 1rem;
}

.asset-address {
  color: #334155; /* Slate 700 */
  font-weight: 600;
  font-size: 1rem;
}

.asset-trade-line {
  font-size: 0.875rem;
  color: #64748B; /* Slate 500 */
  font-weight: 500;
  display: flex;
  align-items: center;
}

.asset-actions {
  flex-shrink: 0;
  margin-left: 1rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.asset-card:hover .asset-actions {
  opacity: 1;
}

.asset-card-body {
  padding-top: 0.75rem;
  border-top: 1px solid #F1F5F9;
  margin-top: 0.25rem;
}

.asset-meta-grid {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.7rem;
  color: #94A3B8; /* Slate 400 */
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.meta-value {
  font-size: 0.95rem;
  color: #0F172A; /* Slate 900 */
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* Breadcrumb link styling */
.breadcrumb-link {
  cursor: pointer;
  transition: color 0.2s ease;
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: #1B3B5F !important; /* Primary navy color */
  text-decoration: underline;
}

.breadcrumb-link:focus {
  outline: 2px solid #1B3B5F;
  outline-offset: 2px;
  border-radius: 2px;
}
</style>
