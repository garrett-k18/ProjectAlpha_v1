<template>
  <!-- WHAT: Performance tab with neutral ledger-style card -->
  <!-- WHY: Summarize purchase costs, expenses, income, and proceeds in one place -->
  <!-- HOW: Placeholder groups ready to wire to backend; minimal chrome per Hyper UI style -->
  <div class="container-fluid px-0">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-body d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-2">
          <i class="fas fa-chart-line text-muted"></i>
          <span class="fw-semibold">Performance Ledger</span>
        </div>
        <div class="d-flex align-items-center gap-2 small text-muted">
          <span>Asset ID:</span>
          <span class="fw-medium">{{ productId ?? row?.asset_hub_id ?? '—' }}</span>
        </div>
      </div>

      <div class="card-body">
        <!-- Single income-statement style table with section headers and subtotals -->
        <div class="table-responsive">
          <table class="table table-sm align-middle mb-0">
            <thead>
              <tr class="text-muted small">
                <th scope="col">Category</th>
                <th scope="col">Item</th>
                <th scope="col" class="text-end">Amount</th>
              </tr>
            </thead>
            <tbody>
              <!-- Purchase Costs -->
              <tr class="table-light">
                <td class="fw-semibold" colspan="3">Purchase Costs</td>
              </tr>
              <tr v-for="(row, i) in data.purchase" :key="'p_'+i">
                <td class="text-muted small">Purchase</td>
                <td>{{ row.label }}</td>
                <td class="text-end">{{ fmtCurrency(row.amount) }}</td>
              </tr>
              <tr v-if="!data.purchase.length">
                <td class="text-muted small" colspan="3">No items yet.</td>
              </tr>
              <tr class="table-light">
                <td class="text-muted">Subtotal</td>
                <td></td>
                <td class="text-end fw-semibold">{{ fmtCurrency(totals.purchase) }}</td>
              </tr>

              <!-- Expenses -->
              <tr class="table-light">
                <td class="fw-semibold" colspan="3">Expenses</td>
              </tr>
              <tr v-for="(row, i) in data.expenses" :key="'e_'+i">
                <td class="text-muted small">Expense</td>
                <td>{{ row.label }}</td>
                <td class="text-end">{{ fmtCurrency(row.amount) }}</td>
              </tr>
              <tr v-if="!data.expenses.length">
                <td class="text-muted small" colspan="3">No items yet.</td>
              </tr>
              <tr class="table-light">
                <td class="text-muted">Subtotal</td>
                <td></td>
                <td class="text-end fw-semibold">{{ fmtCurrency(totals.expenses) }}</td>
              </tr>

              <!-- Income -->
              <tr class="table-light">
                <td class="fw-semibold" colspan="3">Income</td>
              </tr>
              <tr v-for="(row, i) in data.income" :key="'i_'+i">
                <td class="text-muted small">Income</td>
                <td>{{ row.label }}</td>
                <td class="text-end">{{ fmtCurrency(row.amount) }}</td>
              </tr>
              <tr v-if="!data.income.length">
                <td class="text-muted small" colspan="3">No items yet.</td>
              </tr>
              <tr class="table-light">
                <td class="text-muted">Subtotal</td>
                <td></td>
                <td class="text-end fw-semibold">{{ fmtCurrency(totals.income) }}</td>
              </tr>

              <!-- Proceeds -->
              <tr class="table-light">
                <td class="fw-semibold" colspan="3">Proceeds</td>
              </tr>
              <tr v-for="(row, i) in data.proceeds" :key="'pr_'+i">
                <td class="text-muted small">Proceeds</td>
                <td>{{ row.label }}</td>
                <td class="text-end">{{ fmtCurrency(row.amount) }}</td>
              </tr>
              <tr v-if="!data.proceeds.length">
                <td class="text-muted small" colspan="3">No items yet.</td>
              </tr>
              <tr class="table-light">
                <td class="text-muted">Subtotal</td>
                <td></td>
                <td class="text-end fw-semibold">{{ fmtCurrency(totals.proceeds) }}</td>
              </tr>

              <!-- Net -->
              <tr>
                <td colspan="3"></td>
              </tr>
              <tr>
                <td class="fw-semibold">Net</td>
                <td></td>
                <td class="text-end fw-bold">{{ fmtCurrency(netTotal) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Placeholder data model and helpers for Performance ledger
// WHY: Allows wiring to API later while providing immediate UX structure
// NOTE: Keep strong comments per team conventions
import { withDefaults, defineProps, reactive, computed } from 'vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})

// Simple in-memory structure; replace with store/API later
const data = reactive({
  purchase: [] as Array<{ label: string; amount: number }>,
  expenses: [] as Array<{ label: string; amount: number }>,
  income: [] as Array<{ label: string; amount: number }>,
  proceeds: [] as Array<{ label: string; amount: number }>,
})

// Totals per section
const totals = reactive({
  get purchase() { return sum(data.purchase) },
  get expenses() { return sum(data.expenses) },
  get income() { return sum(data.income) },
  get proceeds() { return sum(data.proceeds) },
}) as unknown as Record<string, number>

// Net: income + proceeds - (purchase + expenses)
const netTotal = computed(() => (totals.income + totals.proceeds) - (totals.purchase + totals.expenses))

function sum(rows: Array<{ amount: number }>): number {
  return rows.reduce((acc, r) => acc + (Number(r.amount) || 0), 0)
}

function fmtCurrency(v: number | null | undefined): string {
  const n = Number(v || 0)
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(n)
}
</script>

<style scoped>
.table > :not(caption) > * > * { padding: .375rem .5rem; }
</style>
