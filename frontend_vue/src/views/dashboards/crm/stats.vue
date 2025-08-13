

<template>
  <b-row>
    <b-col md="6" xl="3" v-for="chart of chartData" :key="chart.text">
      <div class="card">
        <div class="card-body">
          <StatChart
              :title="chart.title"
              :number="chart.number"
              :chart-color="chart.chartColor"
              :chart-data="chart.chartData"
              :chart-type="chart.chartType"
              :subtext="chart.subtext"
          />
        </div>
      </div>
    </b-col>
  </b-row>
</template>

<script lang="ts">
import StatChart from '@/components/widgets/widget-stat-chart-1.vue'

export default {
  components: {
    StatChart,
  },
  data() {
    return {
      chartData: [
        {
          title: 'Campaign Sent',
          number: '9,184',
          chartColor: '#727cf5',
          subtext: '3.27%',
          chartData: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54],
          chartType: 'bar',
        },
        {
          title: 'New Leads',
          number: '3,254',
          chartColor: '#0acf97',
          subtext: '5.38%',
          chartData: [25, 66, 41, 89, 63, 25, 44, 12, 36, 9, 54],
          chartType: 'line',
        },
        {
          title: 'Deals',
          number: '861',
          chartColor: '#727cf5',
          subtext: '4.87%',
          chartData: [12, 14, 2, 47, 42, 15, 47, 75, 65, 19, 14],
          chartType: 'bar',
        },
        {
          title: 'Booked Revenue',
          number: '$253k',
          chartColor: '#0acf97',
          subtext: '11.7%',
          chartData: [47, 45, 74, 14, 56, 74, 14, 11, 7, 39, 82],
          chartType: 'bar',
        },
      ],
    }
  },
}
</script>

