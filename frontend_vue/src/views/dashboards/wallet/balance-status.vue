<template>
  <div class="card">
    <div class="card-body pt-0 pb-1">
      <h4 class="header-title mt-3 mb-0">Balance Status</h4>
      <b-tabs pills align="end" lazy>
        <b-tab title="Day" active>
          <div dir="ltr">
            <BaseApexChart :height="350" :series="dayBalanceChart.series" :options="dayBalanceChart.options"/>
          </div>
        </b-tab>
        <b-tab title="Week">
          <div dir="ltr">
            <BaseApexChart :height="350" :series="weekBalanceChart.series" :options="weekBalanceChart.options"/>
          </div>
        </b-tab>
        <b-tab title="Month">
          <div dir="ltr">
            <BaseApexChart :height="350" :series="monthBalanceChart.series" :options="monthBalanceChart.options"/>
          </div>
        </b-tab>
        <b-tab title="Year">
          <div dir="ltr">
            <BaseApexChart :height="350" :series="yearBalanceChart.series" :options="yearBalanceChart.options"/>
          </div>
        </b-tab>
      </b-tabs>

    </div>
  </div>
</template>

<script lang="ts">
import BaseApexChart from "@/components/base-apex-chart.vue";

export default {
  components: {BaseApexChart},
  mounted() {

    this.dayDummyData = this.generateData();
    this.weekDummyData = this.generateData();
    this.monthDummyData = this.generateData();
    this.yearDummyData = this.generateData();

    for (let i = 0; i < 100; i++) {
      let start = new Date();
      this.dayBalanceData.push([start.setDate(start.getDate() + i - 100), this.dayDummyData[i]]);
    }
    for (var i = 0; i < 100; i++) {
      var start = new Date();
      this.weekBalanceData.push([start.setDate(start.getDate() + i * 7 - 100 * 7), this.weekDummyData[i]]);
    }
    for (var i = 0; i < 100; i++) {
      var start = new Date();
      this.monthBalanceData.push([start.setDate(start.getDate() + i * 30 - 100 * 30), this.monthDummyData[i]]);
    }
    for (var i = 0; i < 100; i++) {
      var start = new Date();
      this.yearBalanceData.push([start.setDate(start.getDate() + i * 365 - 100 * 365), this.yearDummyData[i]]);
    }
  },
  data() {
    let dayDummyData, weekDummyData, monthDummyData, yearDummyData
    let dayBalanceData = []
    let weekBalanceData = []
    let monthBalanceData = []
    let yearBalanceData = []
    return {
      dayDummyData,
      dayBalanceData,
      weekDummyData,
      weekBalanceData,
      monthDummyData,
      monthBalanceData,
      yearDummyData,
      yearBalanceData,
      dayBalanceChart: {
        series: [{
          data: dayBalanceData
        }],
        options: {
          chart: {
            type: 'area',
            height: 350,
            toolbar: {
              show: false
            }
          },
          colors: ['#0acf97'],
          dataLabels: {
            enabled: false
          },
          stroke: {
            width: 1,
          },

          markers: {
            size: 0,
            style: 'hollow',
          },
          xaxis: {
            type: 'datetime',
            // min: new Date('01 Mar 2012').getTime(),
            tickAmount: 6,
          },
          yaxis: {
            labels: {
              formatter: function (value) {
                return "$" + value;
              }
            },
          },
          tooltip: {
            x: {
              format: 'dd MMM yyyy'
            }
          },
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.7,
              opacityTo: 0,
              stops: [0, 100]
            }
          },

        }
      },
      weekBalanceChart: {
        series: [{
          data: weekBalanceData
        }],
        options: {
          chart: {
            type: 'area',
            height: 350,
            toolbar: {
              show: false
            }
          },
          colors: ['#0acf97'],
          dataLabels: {
            enabled: false
          },
          stroke: {
            width: 1,
          },

          markers: {
            size: 0,
            style: 'hollow',
          },
          xaxis: {
            type: 'datetime',
            // min: new Date('01 Mar 2012').getTime(),
            tickAmount: 6,
          },
          yaxis: {
            labels: {
              formatter: function (value) {
                return "$" + value;
              }
            },
          },
          tooltip: {
            x: {
              format: 'dd MMM yyyy'
            }
          },
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.7,
              opacityTo: 0,
              stops: [0, 100]
            }
          },

        }
      },
      monthBalanceChart: {
        series: [{
          data: monthBalanceData
        }],
        options: {
          chart: {
            type: 'area',
            height: 350,
            toolbar: {
              show: false
            }
          },
          colors: ['#0acf97'],
          dataLabels: {
            enabled: false
          },
          stroke: {
            width: 1,
          },
          markers: {
            size: 0,
            style: 'hollow',
          },
          xaxis: {
            type: 'datetime',
            // min: new Date('01 Mar 2012').getTime(),
            tickAmount: 6,
          },
          yaxis: {
            labels: {
              formatter: function (value) {
                return "$" + value;
              }
            },
          },
          tooltip: {
            x: {
              format: 'dd MMM yyyy'
            }
          },
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.7,
              opacityTo: 0,
              stops: [0, 100]
            }
          },

        }
      },
      yearBalanceChart: {
        series: [{
          data: yearBalanceData
        },],
        options: {
          chart: {
            type: 'area',
            height: 350,
            toolbar: {
              show: false
            }
          },
          colors: ['#0acf97'],
          dataLabels: {
            enabled: false
          },
          stroke: {
            width: 1,
          },

          markers: {
            size: 0,
            style: 'hollow',
          },
          xaxis: {
            type: 'datetime',
            // min: new Date('01 Mar 2012').getTime(),
            tickAmount: 6,
          },
          yaxis: {
            labels: {
              formatter: function (value) {
                return "$" + value;
              }
            },
          },
          tooltip: {
            x: {
              format: 'dd MMM yyyy'
            }
          },
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.7,
              opacityTo: 0,
              stops: [0, 100]
            }
          },

        }
      }
    }
  },
  methods: {
    generateData() {
      let balanceData = [];
      for (let i = 0; i < 100; i++) {
        balanceData.push(5000 + Math.random() * 100000 + 0.8 * i * i * i)
      }
      return balanceData;
    }
  }
}
</script>