<template>
  <div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="!data || data.length === 0" class="text-center py-5 text-muted">
      <i class="uil uil-coins" style="font-size: 3rem;"></i>
      <p class="mt-2">No accounts</p>
    </div>
    <div v-else class="account-list">
      <div v-for="(account, index) in data" :key="index" class="account-item mb-3 p-2 rounded">
        <div class="d-flex justify-content-between align-items-start">
          <div class="flex-grow-1">
            <div class="fw-bold text-dark">{{ account.account_number }}</div>
            <small class="text-muted">{{ account.account_name }}</small>
          </div>
          <div class="text-end ms-2">
            <div class="fw-bold" :class="getAmountColorClass(account.net_amount)">
              {{ formatCurrency(account.net_amount) }}
            </div>
            <small class="text-muted">{{ account.count }} entries</small>
          </div>
        </div>
        <div class="mt-2">
          <div class="progress" style="height: 4px;">
            <div
              class="progress-bar"
              :class="getProgressColorClass(account.net_amount)"
              :style="{ width: getProgressWidth(account, index) + '%' }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: any[]
  loading: boolean
}>()

const maxAmount = computed(() => {
  if (!props.data || props.data.length === 0) return 1
  return Math.max(...props.data.map(a => Math.abs(parseFloat(a.net_amount) || 0)))
})

function formatCurrency(value: any): string {
  const num = typeof value === 'string' ? parseFloat(value) : value
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num || 0)
}

function getAmountColorClass(amount: any): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (num > 0) return 'text-success'
  if (num < 0) return 'text-danger'
  return 'text-secondary'
}

function getProgressColorClass(amount: any): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (num > 0) return 'bg-success'
  if (num < 0) return 'bg-danger'
  return 'bg-secondary'
}

function getProgressWidth(account: any, index: number): number {
  const amount = Math.abs(parseFloat(account.net_amount) || 0)
  return (amount / maxAmount.value) * 100
}
</script>

<style scoped>
.account-item {
  background-color: #f8f9fa;
  transition: all 0.2s ease;
}

.account-item:hover {
  background-color: #e9ecef;
  transform: translateX(4px);
}
</style>

