<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#fa5c7c","#ffbc00","#39afd1","#0acf97"]
        return {

            series: [{
                    name: "Jan",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Feb",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Mar",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Apr",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "May",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Jun",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Jul",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Aug",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
                {
                    name: "Sep",
                    data: this.generateData(20, {
                        min: -30,
                        max: 55,
                    }),
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "heatmap",
                },
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.5,

                        colorScale: {
                            ranges: [{
                                    from: -30,
                                    to: 5,
                                    name: "Low",
                                    color: colors[0],
                                },
                                {
                                    from: 6,
                                    to: 20,
                                    name: "Medium",
                                    color: colors[1],
                                },
                                {
                                    from: 21,
                                    to: 45,
                                    name: "High",
                                    color: colors[2],
                                },
                                {
                                    from: 46,
                                    to: 55,
                                    name: "Extreme",
                                    color: colors[3],
                                },
                            ],
                        },
                    },
                },
                dataLabels: {
                    enabled: false,
                },
            },
        };
    },
    methods: {
        generateData(
            count: number,
            yrange: {
                min: number;
                max: number;
            }
        ) {
            var i = 0;
            var series = [];
            while (i < count) {
                var x = (i + 1).toString();
                var y =
                    Math.floor(Math.random() * (yrange.max - yrange.min + 1)) +
                    yrange.min;

                series.push({
                    x: x,
                    y: y,
                });
                i++;
            }
            return series;
        },
    },
};
</script>
