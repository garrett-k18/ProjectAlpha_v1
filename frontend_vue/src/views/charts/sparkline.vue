<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>

    <div class="row">
      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Line Charts</h4>

            <div class="mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline1" :series="sparklineChart1.series1"
                                  :option="sparklineChart1.option1"/>
              <BaseSparklineChart id="sparkline1" :series="sparklineChart1.series2"
                                  :option="sparklineChart1.option2"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Bar Chart</h4>

            <div class="mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline2" :series="sparklineChart2.series"
                                  :option="sparklineChart2.option"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Pie Chart</h4>

            <div class="mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline3" :series="sparklineChart3.series"
                                  :option="sparklineChart3.option"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Custom Line Chart</h4>

            <div class="mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline4" :series="sparklineChart4.series1"
                                  :option="sparklineChart4.option1"/>
              <BaseSparklineChart id="sparkline4" :series="sparklineChart4.series2"
                                  :option="sparklineChart4.option2"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Mouse Speed Chart</h4>

            <div class="mt-4" dir="ltr">
              <div id="sparkline5" class="text-center"></div>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Composite bar Chart</h4>

            <div class="text-center mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline6" :series="sparklineChart6.series1"
                                  :option="sparklineChart6.option1"/>
              <BaseSparklineChart id="sparkline6" :series="sparklineChart6.series2"
                                  :option="sparklineChart6.option2"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

      <div class="col-md-6 col-xxl-4">
        <div class="card">
          <div class="card-body">
            <h4 class="header-title">Discrete Chart</h4>

            <div class="text-center mt-4" dir="ltr">
              <BaseSparklineChart id="sparkline7" :series="sparklineChart7.series"
                                  :option="sparklineChart7.option"/>
            </div>
          </div> <!-- end card-body -->
        </div> <!-- card -->
      </div> <!-- end col -->

    </div>
    <!-- end row -->

  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import BaseSparklineChart from "@/components/base-sparkline-chart.vue";

export default {
  components: {BaseSparklineChart, Breadcrumb, Layout},
  data() {
    return {
      title: 'Sparkline Charts',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Charts',
          href: '/',
        },
        {
          text: 'Sparkline Charts',
          active: true,
        },
      ],

      sparklineChart1: {
        series1: [0, 23, 43, 35, 44, 45, 56, 37, 40],
        option1: {
          type: 'line',
          width: "100%",
          height: '165',
          chartRangeMax: 50,
          lineColor: ['#727cf5'],
          fillColor: this.hexToRGB('#727cf5', 0.3),
          highlightLineColor: 'rgba(0,0,0,.1)',
          highlightSpotColor: 'rgba(0,0,0,.2)',
          maxSpotColor: false,
          minSpotColor: false,
          spotColor: false,
          lineWidth: 1
        },
        series2: [25, 23, 26, 24, 25, 32, 30, 24, 19],
        option2: {
          type: 'line',
          width: "100%",
          height: '165',
          chartRangeMax: 40,
          lineColor: ['#0acf97'],
          fillColor: this.hexToRGB('#0acf97', 0.3),
          composite: true,
          highlightLineColor: 'rgba(0,0,0,.1)',
          highlightSpotColor: 'rgba(0,0,0,.2)',
          maxSpotColor: false,
          minSpotColor: false,
          spotColor: false,
          lineWidth: 1
        }
      },
      sparklineChart2: {
        series: [3, 6, 7, 8, 6, 4, 7, 10, 12, 7, 4, 9, 12, 13, 11, 12],
        option: {
          type: 'bar',
          height: '165',
          barWidth: '10',
          barSpacing: '3',
          barColor: ['#39afd1']
        }
      },
      sparklineChart3: {
        series: [20, 40, 30, 10],
        option: {
          type: 'pie',
          width: '165',
          height: '165',
          sliceColors: ['#39afd1', '#ffbc00', '#e3eaef', '#fa5c7c']
        }
      },
      sparklineChart4: {
        series1: [0, 23, 43, 35, 44, 45, 56, 37, 40],
        option1: {
          type: 'line',
          width: "100%",
          height: '165',
          chartRangeMax: 50,
          lineColor: ['#ffbc00'],
          fillColor: 'transparent',
          lineWidth: 2,
          highlightLineColor: 'rgba(0,0,0,.1)',
          highlightSpotColor: 'rgba(0,0,0,.2)',
          maxSpotColor: false,
          minSpotColor: false,
          spotColor: false
        },
        series2: [25, 23, 26, 24, 25, 32, 30, 24, 19],
        option2: {
          type: 'line',
          width: "100%",
          height: '165',
          chartRangeMax: 40,
          lineColor: ['#4eb7eb'],
          fillColor: 'transparent',
          composite: true,
          lineWidth: 2,
          maxSpotColor: false,
          minSpotColor: false,
          spotColor: false,
          highlightLineColor: 'rgba(0,0,0,1)',
          highlightSpotColor: 'rgba(0,0,0,1)'
        }
      },
      sparklineChart6: {
        series1: [3, 6, 7, 8, 6, 4, 7, 10, 12, 7, 4, 9, 12, 13, 11, 12],
        option1: {
          type: 'line',
          width: "100%",
          height: '165',
          lineColor: '#e3eaef',
          lineWidth: 2,
          fillColor: 'rgba(227,234,239,0.3)',
          highlightLineColor: 'rgba(0,0,0,.1)',
          highlightSpotColor: 'rgba(0,0,0,.2)'
        },
        series2: [3, 6, 7, 8, 6, 4, 7, 10, 12, 7, 4, 9, 12, 13, 11, 12],
        option2: {
          type: 'bar',
          height: '165',
          barWidth: '10',
          barSpacing: '5',
          composite: true,
          barColor: '#6c757d'
        }
      },
      sparklineChart7: {
        series: [4, 6, 7, 7, 4, 3, 2, 1, 4, 4, 5, 6, 3, 4, 5, 8, 7, 6, 9, 3, 2, 4, 1, 5, 6, 4, 3, 7],
        option: {
          type: 'discrete',
          width: '280',
          height: '165',
          lineColor: ['#6c757d']
        }
      }
    }
  },
  mounted() {
    this.drawMouseSpeed()
  },
  methods: {
    hexToRGB(hex: any, alpha: any) {
      let r = parseInt(hex.slice(1, 3), 16),
          g = parseInt(hex.slice(3, 5), 16),
          b = parseInt(hex.slice(5, 7), 16);

      if (alpha) {
        return "rgba(" + r + ", " + g + ", " + b + ", " + alpha + ")";
      } else {
        return "rgb(" + r + ", " + g + ", " + b + ")";
      }
    },
    drawMouseSpeed() {
      let mrefreshinterval = 500; // update display every 500ms
      let lastmousex = -1;
      let lastmousey = -1;
      let lastmousetime;
      let mousetravel = 0;
      let mpoints = [];
      let mpoints_max = 30;
      $('html').mousemove(function (e) {
        let mousex = e.pageX;
        let mousey = e.pageY;
        if (lastmousex > -1) {
          mousetravel += Math.max(Math.abs(mousex - lastmousex), Math.abs(mousey - lastmousey));
        }
        lastmousex = mousex;
        lastmousey = mousey;
      });
      let mdraw = function () {
        let md = new Date();
        let timenow = md.getTime();
        if (lastmousetime && lastmousetime != timenow) {
          let pps = Math.round(mousetravel / (timenow - lastmousetime) * 1000);
          mpoints.push(pps);
          if (mpoints.length > mpoints_max)
            mpoints.splice(0, 1);
          mousetravel = 0;

          $('#sparkline5').sparkline(mpoints, {
            tooltipSuffix: ' pixels per second',
            type: 'line',
            width: "100%",
            height: '165',
            chartRangeMax: 77,
            maxSpotColor: false,
            minSpotColor: false,
            spotColor: false,
            lineWidth: 1,
            lineColor: '#fa5c7c',
            fillColor: 'rgba(250, 92, 124, 0.3)',
            highlightLineColor: 'rgba(24,147,126,.1)',
            highlightSpotColor: 'rgba(24,147,126,.2)'
          });
        }
        lastmousetime = timenow;
        setTimeout(mdraw, mrefreshinterval);
      }
      // We could use setInterval instead, but I prefer to do it this way
      setTimeout(mdraw, mrefreshinterval);
    }
  }

}
</script>
