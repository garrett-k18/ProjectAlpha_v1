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

export default {
  components: { StatIcon },
  data() {
    return {
      statsData: [
        {
          icon: 'mdi-account-multiple',
          number: '36,254',
          title: 'Active Assets',
          color: 'success',
          subtext: '5.27%',
        },
        {
          icon: 'mdi mdi-cart-plus',
          number: '5,543',
          title: 'Liquidated Assets',
          color: 'danger',
          subtext: '1.08%',
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
}
</script>