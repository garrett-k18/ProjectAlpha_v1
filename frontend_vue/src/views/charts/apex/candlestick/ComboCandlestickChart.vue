<template>
  <apexchart type="candlestick" height="240" :options="options" :series="series"></apexchart>
  <apexchart type="bar" height="160" :options="options1" :series="series1"></apexchart>
</template>

<script lang="ts">
import {seriesData, seriesDataLinear} from './data'

export default {
  data: function () {
    const colors = ["#0acf97", "#fa5c7c"];
    const barColor = ["#727cf5", "#ffbc00"];
    return {
      series: [{
        data: seriesData
      }],
      options: {
        chart: {
          height: 240,
          type: 'candlestick',
          toolbar: {
            show: false
          },
          zoom: {
            enabled: false
          },
        },
        plotOptions: {
          candlestick: {
            colors: {
              upward: colors[0],
              downward: colors[1]
            }
          }
        },
        xaxis: {
          type: 'datetime'
        },
        grid: {
          borderColor: '#f1f3fa'
        }
      },
      series1: [{
        name: 'volume',
        data: seriesDataLinear
      }],
      options1: {
        chart: {
          height: 160,
          type: 'bar',
          toolbar: {
            show: false,
            autoSelected: 'selection'
          },
          selection: {
            xaxis: {
              min: new Date('20 Jan 2017').getTime(),
              max: new Date('10 Dec 2017').getTime()
            },
            fill: {
              color: '#6c757d',
              opacity: 0.4
            },
            stroke: {
              color: '#6c757d',
            }
          },
          events: {
            selection: function (chart, e) {
              // chartCandlestick.updateOptions({
              //   xaxis: {
              //     min: e.xaxis.min,
              //     max: e.xaxis.max
              //   }
              // }, false, false)
            }
          },

        },
        dataLabels: {
          enabled: false
        },
        plotOptions: {
          bar: {
            columnWidth: '80%',
            colors: {
              ranges: [{
                from: -1000,
                to: 0,
                color: barColor[0],
              }, {
                from: 1,
                to: 10000,
                color: barColor[1]
              }],

            },
          }
        },
        xaxis: {
          type: 'datetime',
          axisBorder: {
            offsetX: 13
          }
        },
        yaxis: {
          labels: {
            show: false
          }
        },
        grid: {
          borderColor: '#f1f3fa'
        }
      }
    }
  }
}
</script>
