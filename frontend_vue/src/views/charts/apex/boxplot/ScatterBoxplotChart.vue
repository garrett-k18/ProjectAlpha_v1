<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#fa5c7c", "#6c757d"];
        return {
            series: [{
                    name: "Box",
                    type: "boxPlot",
                    data: [{
                            x: new Date("2017-01-01").getTime(),
                            y: [54, 66, 69, 75, 88],
                        },
                        {
                            x: new Date("2018-01-01").getTime(),
                            y: [43, 65, 69, 76, 81],
                        },
                        {
                            x: new Date("2019-01-01").getTime(),
                            y: [31, 39, 45, 51, 59],
                        },
                        {
                            x: new Date("2020-01-01").getTime(),
                            y: [39, 46, 55, 65, 71],
                        },
                        {
                            x: new Date("2021-01-01").getTime(),
                            y: [29, 31, 35, 39, 44],
                        },
                    ],
                },
                {
                    name: "Outliers",
                    type: "scatter",
                    data: [{
                            x: new Date("2017-01-01").getTime(),
                            y: 32,
                        },
                        {
                            x: new Date("2018-01-01").getTime(),
                            y: 25,
                        },
                        {
                            x: new Date("2019-01-01").getTime(),
                            y: 64,
                        },
                        {
                            x: new Date("2020-01-01").getTime(),
                            y: 27,
                        },
                        {
                            x: new Date("2020-01-01").getTime(),
                            y: 78,
                        },
                        {
                            x: new Date("2021-01-01").getTime(),
                            y: 15,
                        },
                    ],
                },
            ],
            options: {
                chart: {
                    type: "boxPlot",
                    height: 350,
                },
                colors: colors,
                stroke: {
                    colors: ["#a1a9b1"],
                },
                legend: {
                    offsetY: 10,
                },
                xaxis: {
                    type: "datetime",
                    tooltip: {
                        formatter: function (val: string) {
                            return new Date(val).getFullYear();
                        },
                    },
                },
                grid: {
                    padding: {
                        bottom: 5,
                    },
                },
                tooltip: {
                    shared: false,
                    intersect: true,
                },
                plotOptions: {
                    boxPlot: {
                        colors: {
                            upper: colors[0],
                            lower: colors[1],
                        },
                    },
                },
            },
        };
    },
};
</script>
