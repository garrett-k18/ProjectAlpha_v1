<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Metric 1",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 2",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 3",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 4",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 5",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 6",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 7",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 8",
                    data: this.generateData(20, {
                        min: 0,
                        max: 90,
                    }),
                },
                {
                    name: "Metric 9",
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
                dataLabels: {
                    enabled: false,
                },
                colors: ["#F3B415", "#F27036", "#663F59", "#6A6E94", "#4E88B4", "#00A7C6", "#18D8D8", "#A9D794", "#46AF78"],

                xaxis: {
                    type: "category",
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
