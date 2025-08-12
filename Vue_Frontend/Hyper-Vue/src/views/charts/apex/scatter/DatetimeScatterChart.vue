<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            options: {
                chart: {
                    height: 380,
                    type: "scatter",
                    zoom: {
                        type: "xy",
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                colors: ["#6c757d", "#ffbc00", "#727cf5", "#0acf97", "#fa5c7c"],
                grid: {
                    borderColor: "#f1f3fa",
                    padding: {
                        bottom: 5,
                    },
                    xaxis: {
                        showLines: true,
                    },
                    yaxis: {
                        showLines: true,
                    },
                },
                legend: {
                    offsetY: 10,
                },
                xaxis: {
                    type: "datetime",
                },
                yaxis: {
                    max: 70,
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        chart: {
                            toolbar: {
                                show: false,
                            },
                        },
                        legend: {
                            show: false,
                        },
                    },
                }, ],
            },
            series: [{
                    name: "Team 1",
                    data: this.generateDayWiseTimeSeries(
                        new Date("11 Feb 2017 GMT").getTime(),
                        20, {
                            min: 10,
                            max: 60,
                        }
                    ),
                },
                {
                    name: "Team 2",
                    data: this.generateDayWiseTimeSeries(
                        new Date("11 Feb 2017 GMT").getTime(),
                        20, {
                            min: 10,
                            max: 60,
                        }
                    ),
                },
                {
                    name: "Team 3",
                    data: this.generateDayWiseTimeSeries(
                        new Date("11 Feb 2017 GMT").getTime(),
                        30, {
                            min: 10,
                            max: 60,
                        }
                    ),
                },
                {
                    name: "Team 4",
                    data: this.generateDayWiseTimeSeries(
                        new Date("11 Feb 2017 GMT").getTime(),
                        10, {
                            min: 10,
                            max: 60,
                        }
                    ),
                },
                {
                    name: "Team 5",
                    data: this.generateDayWiseTimeSeries(
                        new Date("11 Feb 2017 GMT").getTime(),
                        30, {
                            min: 10,
                            max: 60,
                        }
                    ),
                },
            ],
        };
    },
    methods: {
        generateDayWiseTimeSeries(baseval: number, count: number, yrange: { max: number, min: number }) {
            var i = 0;
            var series = [];
            while (i < count) {
                var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

                series.push([baseval, y]);
                baseval += 86400000;
                i++;
            }
            return series;
        }
    }
};
</script>
