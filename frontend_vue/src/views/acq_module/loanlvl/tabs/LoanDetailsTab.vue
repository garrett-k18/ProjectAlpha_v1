<template>
  <div class="px-3 px-lg-4">
    <div class="row g-3">
      <div class="col-12 col-lg-6 col-xl-4">
        <LoanDetails :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <TotalDebt :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <Origination :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <Foreclosure :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <Bankruptcy :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <LossMitigation :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <RehabHoldbacks :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
      <div class="col-12 col-lg-6 col-xl-4">
        <ServicingNotes :row="row" :productId="productId" class="h-100 d-flex flex-column" />
      </div>
    </div>

    <!-- Trailing 12 Months Cash Flow: full-width row below -->
    <div class="row g-3 mt-1">
      <div class="col-12">
        <T12CashFlow :asOf="new Date()" />
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
import LoanDetails from '@/views/acq_module/loanlvl/components/loandetails.vue'
import TotalDebt from '@/views/acq_module/loanlvl/components/totaldebt.vue'
import Origination from '@/views/acq_module/loanlvl/components/origination.vue'
import Foreclosure from '@/views/acq_module/loanlvl/components/foreclosure.vue'
import Bankruptcy from '@/views/acq_module/loanlvl/components/bankruptcy.vue'
import LossMitigation from '@/views/acq_module/loanlvl/components/lossmitigation.vue'
import T12CashFlow from '@/views/acq_module/loanlvl/components/t12cashflow.vue'
import RehabHoldbacks from '@/views/acq_module/loanlvl/components/rehabholdbacks.vue'
import ServicingNotes from '@/views/acq_module/loanlvl/components/servicingnotes.vue'

withDefaults(defineProps<{
  row?: Record<string, any> | null
  productId?: string | number | null
}>(), {
  row: null,
  productId: null,
})
</script>
