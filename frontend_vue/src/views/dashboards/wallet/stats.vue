<template>
  <b-row>
    <b-col xl="4" v-for="(chart,index) in chartData" :key="index">
      <StatChart
          :icon="chart.icon"
          :amount="chart.amount"
          :growth="chart.growth"
          :growth-icon="chart.growthIcon"
          :rate="chart.rate"
          :chart-data="chart.chartData"
          :chart-type="chart.chartType"
          :chart-color="chart.chartColor"
      />
    </b-col>
  </b-row>
</template>

<script lang="ts">
import StatChart from '@/components/widgets/widget-stat-chart-2.vue'

export default {
  components: {StatChart},
  data() {
    return {
      chartData: [
        {
          icon: 'mdi-currency-btc',
          amount: '12,500',
          growth: 45,
          growthIcon: 'mdi-arrow-up-bold',
          rate: '1.00 BTC = $48,781.20',
          chartData: [25, 33, 28, 35, 30, 40],
          chartType: 'line',
          chartColor: '#727cf5'
        },
        {
          icon: 'mdi-currency-cny',
          amount: '9,250',
          growth: 32,
          growthIcon: 'mdi-arrow-up-bold',
          rate: '1.00 CNY = $0.6',
          chartData: [25, 44, 12, 36, 9, 54, 25, 66, 41, 89, 63],
          chartType: 'bar',
          chartColor: '#727cf5'
        },
        {
          icon: 'mdi-currency-eth',
          amount: '12,500',
          growth: 60,
          growthIcon: 'mdi-arrow-up-bold',
          rate: '1.00 ETH = $3,783.68',
          chartData: [25, 33, 28, 35, 30, 40],
          chartType: 'line',
          chartColor: '#727cf5'
        },
      ]
    }
  }
}
</script>