<template>
  <!-- AM Loan Details: composes loan detail subcomponents -->
  <b-row class="g-3 g-lg-4 px-3 px-lg-4">
    <b-col lg="6" class="d-flex">
      <LoanDetails class="w-100" :row="row" :productId="productId" />
    </b-col>
    <b-col lg="6" class="d-flex">
      <TotalDebt class="w-100" :row="row" :productId="productId" />
    </b-col>

    <b-col lg="6" class="d-flex">
      <Origination class="w-100" :row="row" :productId="productId" />
    </b-col>
    <b-col lg="6" class="d-flex">
      <Foreclosure class="w-100" :row="row" :productId="productId" />
    </b-col>

    <b-col lg="6" class="d-flex">
      <Bankruptcy class="w-100" :row="row" :productId="productId" />
    </b-col>
    <b-col lg="6" class="d-flex">
      <LossMitigation class="w-100" :row="row" :productId="productId" />
    </b-col>

    <b-col lg="6" class="d-flex">
      <RehabHoldbacks class="w-100" :row="row" :productId="productId" />
    </b-col>
    <b-col lg="6" class="d-flex">
      <ServicingNotes class="w-100" :row="row" :productId="productId" />
    </b-col>

    <b-col lg="12" class="d-flex">
      <T12CashFlow class="w-100" :row="row" :productId="productId" />
    </b-col>
  </b-row>
</template>

<script setup lang="ts">
import { withDefaults, defineProps } from 'vue'
// Reuse the existing components which render from provided row
import LoanDetails from '@/views/acq_module/loanlvl/components/loandetails.vue'
import TotalDebt from '@/views/acq_module/loanlvl/components/totaldebt.vue'
import Origination from '@/views/acq_module/loanlvl/components/origination.vue'
import Foreclosure from '@/views/acq_module/loanlvl/components/foreclosure.vue'
import Bankruptcy from '@/views/acq_module/loanlvl/components/bankruptcy.vue'
import LossMitigation from '@/views/acq_module/loanlvl/components/lossmitigation.vue'
import RehabHoldbacks from '@/views/acq_module/loanlvl/components/rehabholdbacks.vue'
import ServicingNotes from '@/views/acq_module/loanlvl/components/servicingnotes.vue'
import T12CashFlow from '@/views/acq_module/loanlvl/components/t12cashflow.vue'

withDefaults(defineProps<{ row?: Record<string, any> | null; productId?: string | number | null }>(), {
  row: null,
  productId: null,
})
</script>
