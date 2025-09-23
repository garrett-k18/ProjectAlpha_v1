<template>
  <!-- As-Of banner (outside cards) -->
  <div class="px-3 px-lg-4 pb-1 text-muted ms-2 ms-lg-2"><small><em>As Of Date: {{ formatDate(servicerData?.as_of || servicerData?.as_of_date) }}</em></small></div>

  <!-- AM Loan Details: composes loan detail subcomponents -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="4" class="d-flex">
      <LoanDetails class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
    <b-col lg="4" class="d-flex">
      <TotalDebt class="w-100" :row="servicerData" :productId="productId" />
    </b-col>

    <b-col lg="4" class="d-flex">
      <Origination class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
    <b-col lg="4" class="d-flex">
      <Borrower class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
    <b-col lg="4" class="d-flex">
      <Foreclosure class="w-100" :row="servicerData" :productId="productId" />
    </b-col>

    <b-col lg="4" class="d-flex">
      <Bankruptcy class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
    <b-col lg="4" class="d-flex">
      <LossMitigation class="w-100" :row="servicerData" :productId="productId" />
    </b-col>

    <b-col lg="4" class="d-flex">
      <RehabHoldbacks class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
    <b-col lg="4" class="d-flex">
      <ServicingNotes class="w-100" :row="servicerData" :productId="productId" />
    </b-col>

    <b-col lg="12" class="d-flex">
      <T12CashFlow class="w-100" :row="servicerData" :productId="productId" />
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed, ref, watch } from 'vue'
import http from '@/lib/http'
// Use AM-specific cards (can diverge field names freely)
import LoanDetails from '@/views/am_module/loanlvl/components/loandetails.vue'
import TotalDebt from '@/views/am_module/loanlvl/components/totaldebt.vue'
import Origination from '@/views/am_module/loanlvl/components/origination.vue'
import Borrower from '@/views/am_module/loanlvl/components/borrower.vue'
import Foreclosure from '@/views/am_module/loanlvl/components/foreclosure.vue'
import Bankruptcy from '@/views/am_module/loanlvl/components/bankruptcy.vue'
import LossMitigation from '@/views/am_module/loanlvl/components/lossmitigation.vue'
import RehabHoldbacks from '@/views/am_module/loanlvl/components/rehabholdbacks.vue'
import ServicingNotes from '@/views/am_module/loanlvl/components/servicingnotes.vue'
import T12CashFlow from '@/views/am_module/loanlvl/components/t12cashflow.vue'

// Single defineProps with defaults (avoid duplicate defineProps error)
const props = withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})

// Fetch latest ServicerLoanData from dedicated endpoint
const servicerData = ref<Record<string, any> | null>(null)
watch(
  () => props.productId,
  async (raw) => {
    const id = raw != null ? Number(raw) : NaN
    if (!Number.isFinite(id)) { servicerData.value = null; return }
    try {
      const { data } = await http.get(`/am/assets/${id}/servicing/`)
      servicerData.value = data && Object.keys(data).length ? data : null
    } catch (e) {
      servicerData.value = null
    }
  },
  { immediate: true }
)

function formatDate(v:any): string { return v ? new Date(v).toLocaleDateString('en-US') : 'N/A' }
</script>
