<template>
  <!--
    Macro Rates Widget
    Displays key economic indicators (mortgage rates, etc.) from FRED API
    Shows current rate and percentage change from previous period
  -->
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">
        <i class="mdi mdi-chart-line me-2"></i>
        Market Indicators
      </h5>
    </div>
    <div class="card-body">
      <!-- Loading State -->
      <div v-if="loading && rates.length === 0" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger mb-0">
        <i class="mdi mdi-alert-circle-outline me-2"></i>
        {{ error }}
      </div>

      <!-- Rates List -->
      <ul v-else class="list-unstyled mb-0">
        <li 
          v-for="(rate, idx) in rates" 
          :key="idx" 
          class="d-flex justify-content-between align-items-center py-2"
          :class="{ 'border-bottom': idx < rates.length - 1 }"
        >
          <!-- Left: Indicator Name & Icon -->
          <div class="d-flex align-items-center">
            <div class="avatar-xs me-2 flex-shrink-0">
              <span class="avatar-title rounded-circle" :class="rate.iconBg">
                <i :class="rate.icon" class="text-white"></i>
              </span>
            </div>
            <div>
              <div class="fw-semibold small">{{ rate.name }}</div>
              <small class="text-muted" style="font-size: 0.7rem;">{{ rate.date }}</small>
            </div>
          </div>

          <!-- Right: Rate Value & Change -->
          <div class="text-end">
            <div class="fw-bold">{{ rate.value }}%</div>
            <small 
              v-if="rate.change !== null" 
              :class="rate.changeClass"
              class="fw-semibold"
            >
              <i :class="rate.changeIcon"></i>
              {{ rate.changeText }}
            </small>
            <small v-else class="text-muted">—</small>
          </div>
        </li>
      </ul>

    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from '@/lib/http';

export interface RateData {
  name: string;
  value: string;
  date: string;
  change: number | null;
  changeText: string;
  changeClass: string;
  changeIcon: string;
  icon: string;
  iconBg: string;
  previousRate?: number | null;
  previousDate?: string | null;
}

export default defineComponent({
  name: 'MacroRatesWidget',
  
  data() {
    return {
      rates: [] as RateData[],
      loading: false,
      error: null as string | null,
    };
  },

  mounted() {
    // Fetch rates on component mount
    this.fetchRates();
  },

  methods: {
    /**
     * Fetch macro rates from backend API
     */
    async fetchRates() {
      this.loading = true;
      this.error = null;

      try {
        // Fetch all economic indicators from FRED API in order: SOFR, Fed Funds, 30yr Mortgage, 10yr Treasury, CPI
        const [sofrRes, fedFundsRes, mortgage30Res, treasury10Res, cpiRes] = await Promise.all([
          axios.get('/api/core/macro/sofr/'),
          axios.get('/api/core/macro/fed-funds-rate/'),
          axios.get('/api/core/macro/mortgage-rates/30-year/'),
          axios.get('/api/core/macro/10-year-treasury/'),
          axios.get('/api/core/macro/cpi/'),
        ]);

        const rates = [];

        // SOFR (Secured Overnight Financing Rate)
        if (sofrRes.data) {
          const data = sofrRes.data;
          rates.push({
            name: 'SOFR',
            value: data.value ? data.value.toFixed(2) : 'N/A',
            date: this.formatDate(data.date),
            change: data.change_pct,
            changeText: data.change_pct !== null ? `${data.change_pct >= 0 ? '+' : ''}${data.change_pct.toFixed(2)}%` : '',
            changeClass: data.change_pct !== null ? (data.change_pct >= 0 ? 'text-danger' : 'text-success') : '',
            changeIcon: data.change_pct !== null ? (data.change_pct >= 0 ? 'mdi mdi-arrow-up' : 'mdi mdi-arrow-down') : '',
            icon: 'mdi mdi-currency-usd',
            iconBg: 'bg-secondary',
            previousRate: data.previous_value,
            previousDate: data.previous_date ? this.formatDate(data.previous_date) : null,
          });
        }

        // Fed Funds Rate
        if (fedFundsRes.data) {
          const data = fedFundsRes.data;
          rates.push({
            name: 'Fed Funds',
            value: data.value ? data.value.toFixed(2) : 'N/A',
            date: this.formatDate(data.date),
            change: data.change_pct,
            changeText: data.change_pct !== null ? `${data.change_pct >= 0 ? '+' : ''}${data.change_pct.toFixed(2)}%` : '',
            changeClass: data.change_pct !== null ? (data.change_pct >= 0 ? 'text-danger' : 'text-success') : '',
            changeIcon: data.change_pct !== null ? (data.change_pct >= 0 ? 'mdi mdi-arrow-up' : 'mdi mdi-arrow-down') : '',
            icon: 'mdi mdi-bank',
            iconBg: 'bg-info',
            previousRate: data.previous_value,
            previousDate: data.previous_date ? this.formatDate(data.previous_date) : null,
          });
        }

        // 30-Year Mortgage
        if (mortgage30Res.data) {
          const data = mortgage30Res.data;
          rates.push({
            name: '30-Year Mortgage',
            value: data.rate ? data.rate.toFixed(2) : 'N/A',
            date: this.formatDate(data.date),
            change: data.change_pct,
            changeText: data.change_pct !== null ? `${data.change_pct >= 0 ? '+' : ''}${data.change_pct.toFixed(2)}%` : '',
            changeClass: data.change_pct !== null ? (data.change_pct >= 0 ? 'text-danger' : 'text-success') : '',
            changeIcon: data.change_pct !== null ? (data.change_pct >= 0 ? 'mdi mdi-arrow-up' : 'mdi mdi-arrow-down') : '',
            icon: 'mdi mdi-home-variant',
            iconBg: 'bg-primary',
            previousRate: data.previous_rate,
            previousDate: data.previous_date ? this.formatDate(data.previous_date) : null,
          });
        }

        // 10-Year Treasury
        if (treasury10Res.data) {
          const data = treasury10Res.data;
          rates.push({
            name: '10-Yr Treasury',
            value: data.value ? data.value.toFixed(2) : 'N/A',
            date: this.formatDate(data.date),
            change: data.change_pct,
            changeText: data.change_pct !== null ? `${data.change_pct >= 0 ? '+' : ''}${data.change_pct.toFixed(2)}%` : '',
            changeClass: data.change_pct !== null ? (data.change_pct >= 0 ? 'text-danger' : 'text-success') : '',
            changeIcon: data.change_pct !== null ? (data.change_pct >= 0 ? 'mdi mdi-arrow-up' : 'mdi mdi-arrow-down') : '',
            icon: 'mdi mdi-chart-bell-curve',
            iconBg: 'bg-success',
            previousRate: data.previous_value,
            previousDate: data.previous_date ? this.formatDate(data.previous_date) : null,
          });
        }

        // CPI (Consumer Price Index)
        if (cpiRes.data) {
          const data = cpiRes.data;
          rates.push({
            name: 'CPI',
            value: data.value ? data.value.toFixed(1) : 'N/A',
            date: this.formatDate(data.date),
            change: data.change_pct,
            changeText: data.change_pct !== null ? `${data.change_pct >= 0 ? '+' : ''}${data.change_pct.toFixed(2)}%` : '',
            changeClass: data.change_pct !== null ? (data.change_pct >= 0 ? 'text-danger' : 'text-success') : '',
            changeIcon: data.change_pct !== null ? (data.change_pct >= 0 ? 'mdi mdi-arrow-up' : 'mdi mdi-arrow-down') : '',
            icon: 'mdi mdi-cart',
            iconBg: 'bg-warning',
            previousRate: data.previous_value,
            previousDate: data.previous_date ? this.formatDate(data.previous_date) : null,
          });
        }

        this.rates = rates;
      } catch (err: any) {
        console.error('Failed to fetch macro rates:', err);
        this.error = err.response?.data?.error || 'Failed to load market indicators';
      } finally {
        this.loading = false;
      }
    },

    

    /**
     * Format date string to readable format
     */
    formatDate(dateStr: string): string {
      if (!dateStr) return '';
      
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric' 
        });
      } catch {
        return dateStr;
      }
    },
  },
});
</script>

<style scoped>
/* Compact card styling */
.card {
  font-size: 0.9rem;
}

.card-header {
  padding: 0.75rem 1rem;
}

.card-body {
  padding: 0.75rem 1rem;
}

/* Smaller avatar icons */
.avatar-xs {
  height: 2rem;
  width: 2rem;
}

.avatar-xs .avatar-title {
  font-size: 0.875rem;
}

/* Hover effect for list items */
li:hover {
  background-color: rgba(0, 0, 0, 0.02);
  transition: background-color 0.2s ease;
}
</style>
