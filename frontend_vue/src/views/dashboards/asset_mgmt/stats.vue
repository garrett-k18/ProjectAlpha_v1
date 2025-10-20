<template>
  <b-row>
    <b-col sm="6" v-for="widget of statsData" :key="widget.title">
      <StatIcon
          :icon="widget.icon"
          :title="widget.title"
          :number="widget.number"
          :subtext="widget.subtext"
          :color="widget.color"
      />
    </b-col>
  </b-row>
</template>

<script>
import StatIcon from '@/components/widgets/widget-stat-icon.vue'
import http from '@/lib/http'

export default {
  components: { StatIcon },
  data() {
    return {
      isLoading: false,
      statsData: [
        {
          icon: 'mdi-account-multiple',
          number: '0',
          title: 'Active Assets',
          color: 'success',
          subtext: 'Live count',
        },
        {
          icon: 'mdi mdi-cart-plus',
          number: '0',
          title: 'Liquidated Assets',
          color: 'danger',
          subtext: 'Live count',
        },
        {
          icon: 'mdi-currency-usd',
          number: '$6,254',
          title: 'Revenue',
          color: 'danger',
          subtext: '7.00%',
        },
        {
          icon: 'mdi-pulse widget-icon',
          number: '+ 30.56%',
          title: 'Growth',
          color: 'success',
          subtext: '4.87%',
        },
      ],
    }
  },
  methods: {
    formatNumber(value) {
      return new Intl.NumberFormat('en-US').format(value)
    },
    setWidgetNumber(title, rawValue) {
      const widget = this.statsData.find((item) => item.title === title)
      if (!widget) return
      widget.number = this.formatNumber(rawValue)
    },
    async fetchDashboardStats() {
      this.isLoading = true
      try {
        const { data } = await http.get('/am/dashboard/stats/')
        this.setWidgetNumber('Active Assets', data.active_assets ?? 0)
        this.setWidgetNumber('Liquidated Assets', data.liquidated_assets ?? 0)
      } catch (error) {
        console.error('Failed to load asset dashboard stats', error)
      } finally {
        this.isLoading = false
      }
    },
  },
  mounted() {
    this.fetchDashboardStats()
  },
}
</script>