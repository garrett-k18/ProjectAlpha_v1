<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#0acf97", "#ffbc00"];
        return {
            series: [{
                    name: "Metric1",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric2",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric3",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric4",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric5",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric6",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric7",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric8",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric8",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "heatmap",
                },
                stroke: {
                    width: 0,
                },
                plotOptions: {
                    heatmap: {
                        radius: 30,
                        enableShades: false,
                        colorScale: {
                            ranges: [{
                                    from: 0,
                                    to: 50,
                                    color: colors[0],
                                },
                                {
                                    from: 51,
                                    to: 100,
                                    color: colors[1],
                                },
                            ],
                        },
                    },
                },
                colors: colors,
                dataLabels: {
                    enabled: true,
                    style: {
                        colors: ["#fff"],
                    },
                },
                xaxis: {
                    type: "category",
                },
                grid: {
                    borderColor: "#f1f3fa",
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
