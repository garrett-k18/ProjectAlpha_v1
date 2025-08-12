  <template>
    <b-row>
      <b-col sm="6">
        <apexchart
          type="bar"
          height="380"
          :options="options"
          :series="series"
          @dataPointSelection="dataPointSelectionHandler"
        ></apexchart>
      </b-col>
      <b-col sm="6">
        <apexchart
            type="bar"
            height="380"
            :options="optionsQuarter"
            :series="optionsQuarter.series"
        ></apexchart>
      </b-col>
    </b-row>
  </template>

  <script lang="ts">
  import { arrayData, colors, series, options, optionsQuarter } from "./data";

  export default {
    data() {
      return {
        series,
        options,
        optionsQuarter
      };
    },
    methods:{
      dataPointSelectionHandler(e: any, chart: any, opts: any) {
        this.updateQuarterChart(chart, "barQuarter");
        return;
        let quarterChartEl = document.querySelector("#chart-quarter");
        let yearChartEl = document.querySelector("#chart-year");
        if (opts.selectedDataPoints[0].length === 1) {
          if (quarterChartEl?.classList.contains("active")) {
            this.updateQuarterChart(chart, "barQuarter");
          } else {
            yearChartEl?.classList.add("chart-quarter-activated");
            quarterChartEl?.classList.add("active");
            this.updateQuarterChart(chart, "barQuarter");
          }
        } else {
          this.updateQuarterChart(chart, "barQuarter");
        }
        if (opts.selectedDataPoints[0].length === 0) {
          yearChartEl?.classList.remove("chart-quarter-activated");
          quarterChartEl?.classList.remove("active");
        }
      },
      updateQuarterChart(sourceChart, destChartIDToUpdate) {
        var series = [];
        var seriesIndex = 0;
        var colors = []

        if (sourceChart.w.globals.selectedDataPoints[0]) {
          var selectedPoints = sourceChart.w.globals.selectedDataPoints;
          for (var i = 0; i < selectedPoints[seriesIndex].length; i++) {
            var selectedIndex = selectedPoints[seriesIndex][i];
            var yearSeries = sourceChart.w.config.series[seriesIndex];
            series.push({
              name: yearSeries.data[selectedIndex].x,
              data: yearSeries.data[selectedIndex].quarters
            })
            colors.push(yearSeries.data[selectedIndex].color)
          }

          if (series.length === 0) series = [{
            data: []
          }]

          this.optionsQuarter.series = series;
          this.optionsQuarter.colors = colors;
          this.optionsQuarter.fill.colors = colors;

          return ApexCharts.exec(destChartIDToUpdate, 'updateOptions', {
            series: series,
            colors: colors,
            fill: {
              colors: colors
            }
          })
        }
      }
    }


  };
  </script>
