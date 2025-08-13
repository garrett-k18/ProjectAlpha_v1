<template>
<apexchart height="160" :options="options" :series="series"></apexchart>
<apexchart height="200" :options="options1" :series="series1"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                data: this.generateDayWiseTimeSeries(
                    new Date("11 Feb 2017").getTime(),
                    20, {
                        min: 10,
                        max: 30,
                    }
                ),
            }, ],
            options: {
                chart: {
                    type: "line",
                    height: 160,
                    id: "fb",
                    group: "social",
                },
                colors: ["#727cf5"],
                stroke: {
                    width: [3],
                    curve: "straight",
                },
                toolbar: {
                    tools: {
                        selection: false,
                    },
                },
                fill: {
                    opacity: 1,
                },
                tooltip: {
                    followCursor: false,
                    theme: "dark",
                    x: {
                        show: false,
                    },
                    marker: {
                        show: false,
                    },
                    y: {
                        title: {
                            formatter: function () {
                                return "";
                            },
                        },
                    },
                },

                xaxis: {
                    type: "datetime",
                },
                grid: {
                    row: {
                        colors: ["transparent", "transparent"], // takes an array which will be repeated on columns
                        opacity: 0.2,
                    },
                    borderColor: "#f1f3fa",
                },
            },

            series1: [{
                data: this.generateDayWiseTimeSeries(
                    new Date("11 Feb 2017").getTime(),
                    20, {
                        min: 10,
                        max: 60,
                    }
                ),
            }, ],
            options1: {
                chart: {
                    height: 200,
                    type: "line",
                    id: "yt",
                    group: "social",
                },
                colors: ["#6c757d"],
                dataLabels: {
                    enabled: false,
                },
                toolbar: {
                    tools: {
                        selection: false,
                    },
                },
                tooltip: {
                    followCursor: false,
                    theme: "dark",
                    x: {
                        show: false,
                    },
                    marker: {
                        show: false,
                    },
                    y: {
                        title: {
                            formatter: function () {
                                return "";
                            },
                        },
                    },
                },
                stroke: {
                    width: [3],
                    curve: "smooth",
                },

                fill: {
                    gradient: {
                        enabled: true,
                        opacityFrom: 0.6,
                        opacityTo: 0.8,
                    },
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                },
                xaxis: {
                    type: "datetime",
                },
                grid: {
                    row: {
                        colors: ["transparent", "transparent"], // takes an array which will be repeated on columns
                        opacity: 0.2,
                    },
                    borderColor: "#f1f3fa",
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
