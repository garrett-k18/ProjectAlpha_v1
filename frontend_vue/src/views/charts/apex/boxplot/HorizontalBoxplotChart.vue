<template>
  <apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
  data() {
    const colors = ["#727cf5", "#0acf97", "#e3eaef"];
    return {
      series: [{
        data: [{
          x: "Category A",
          y: [54, 66, 69, 75, 88],
        },
          {
            x: "Category B",
            y: [43, 65, 69, 76, 81],
          },
          {
            x: "Category C",
            y: [31, 39, 45, 51, 59],
          },
          {
            x: "Category D",
            y: [39, 46, 55, 65, 71],
          },
          {
            x: "Category E",
            y: [29, 31, 35, 39, 44],
          },
          {
            x: "Category F",
            y: [41, 49, 58, 61, 67],
          },
          {
            x: "Category G",
            y: [54, 59, 66, 71, 88],
          },
        ],
      },],
      options: {
        chart: {
          type: "boxPlot",
          height: 350,
        },
        plotOptions: {
          bar: {
            horizontal: true,
            barHeight: "50%",
          },
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
