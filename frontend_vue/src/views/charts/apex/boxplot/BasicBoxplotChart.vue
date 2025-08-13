<template>
  <apexchart type="boxPlot" height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
  data() {
    const colors = ["#727cf5", "#0acf97"]
    return {
      series: [
        {
          type: "boxPlot",
          data: [
            {
              x: "Jan 2015",
              y: [54, 66, 69, 75, 88],
            },
            {
              x: "Jan 2016",
              y: [43, 65, 69, 76, 81],
            },
            {
              x: "Jan 2017",
              y: [31, 39, 45, 51, 59],
            },
            {
              x: "Jan 2018",
              y: [39, 46, 55, 65, 71],
            },
            {
              x: "Jan 2019",
              y: [29, 31, 35, 39, 44],
            },
            {
              x: "Jan 2020",
              y: [41, 49, 58, 61, 67],
            },
            {
              x: "Jan 2021",
              y: [54, 59, 66, 71, 88],
            },
          ],
        },],
      options: {
        chart: {
          type: "boxPlot",
          height: 350,
          toolbar: {
            show: false,
          },
          event: {}
        },
        plotOptions: {
          boxPlot: {
            colors: {
              upper: colors[0],
              lower: colors[1],
            },
          },
        },
        stroke: {
          colors: ["#a1a9b1"],
        },
      },
    };
  },
};
</script>
