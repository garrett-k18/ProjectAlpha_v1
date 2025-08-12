<template>
  <canvas id="boundaries-example"></canvas>
</template>

<script lang="ts">
import Chart, {type ChartItem, type ChartTypeRegistry} from 'chart.js/auto';
import {hexToRGB} from '../utility';

export default {
  data() {
    let chart;
    const colors = ["#3e60d5", "#47ad77"]
    const config = {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'March', 'April', 'May', 'June'], datasets: [{
          label: 'Fully Rounded',
          data: [12.5, -19.4, 14.3, -15.0, 10.8, -10.5],
          borderColor: colors[0],
          backgroundColor: hexToRGB(colors[0], .3),
          fill: false
        },]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,

            position: 'top',
          },

        }, scales: {
          x: {
            grid: {
              display: false
            }
          }, y: {
            grid: {
              display: false
            }
          },
        }
      },
    }
    return {
      chart,
      config
    }
  },
  mounted() {
    const canvasTag = <ChartItem>document.getElementById('boundaries-example')
    this.chart = new Chart(canvasTag, this.config)
  },
  unmounted() {
    this.chart.clear()
  }
}
</script>
