<template>
<apexchart height="230" id="chart1" :options="chartOptions" :series="series"></apexchart>
<apexchart height="130" :options="chartOptionsLine" :series="seriesLine"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                data: this.generateDayWiseTimeSeries(
                    new Date("11 Feb 2017").getTime(),
                    185, {
                        min: 30,
                        max: 90,
                    }
                ),
            }, ],
            chartOptions: {
                chart: {
                    id: "chart1",
                    type: "line",
                    height: 230,
                    toolbar: {
                        autoSelected: "pan",
                        show: false,
                    },
                },
                colors: ["#3e60d5"],
                stroke: {
                    width: 3,
                },
                dataLabels: {
                    enabled: false,
                },
                fill: {
                    opacity: 1,
                },
                markers: {
                    size: 0,
                },
                xaxis: {
                    type: "datetime",
                },
            },
            seriesLine: [{
                data: this.generateDayWiseTimeSeries(
                    new Date("11 Feb 2017").getTime(),
                    185, {
                        min: 30,
                        max: 90,
                    }
                ),
            }, ],
            chartOptionsLine: {
                chart: {
                    id: "chart2",
                    height: 130,
                    type: "area",
                    brush: {
                        target: "chart1",
                        enabled: true,
                    },
                    selection: {
                        enabled: true,
                        xaxis: {
                            min: new Date("19 Jun 2017").getTime(),
                            max: new Date("14 Aug 2017").getTime(),
                        },
                    },
                },
                colors: ["#39afd1"],
                fill: {
                    type: "gradient",
                    gradient: {
                        opacityFrom: 0.91,
                        opacityTo: 0.1,
                    },
                },
                xaxis: {
                    type: "datetime",
                    tooltip: {
                        enabled: false,
                    },
                },
                yaxis: {
                    tickAmount: 2,
                },
            },
        };
    },
    methods: {
        generateDayWiseTimeSeries(
            baseval: number,
            count: number,
            yrange: { max: number;min: number }
        ) {
            var i = 0;
            var series = [];
            while (i < count) {
                var x = baseval;
                var y =
                    Math.floor(Math.random() * (yrange.max - yrange.min + 1)) +
                    yrange.min;

                series.push([x, y]);
                baseval += 86400000;
                i++;
            }
            return series;
        },
    },
};
</script>
