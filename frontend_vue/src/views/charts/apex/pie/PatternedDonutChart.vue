<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [44, 55, 41, 17, 15],
            options: {
                chart: {
                    height: 320,
                    type: "donut",
                    dropShadow: {
                        enabled: true,
                        color: "#111",
                        top: -1,
                        left: 3,
                        blur: 3,
                        opacity: 0.2,
                    },
                },
                stroke: {
                    show: true,
                    width: 2,
                },
                colors: ["#39afd1", "#ffbc00", "#313a46", "#fa5c7c", "#0acf97"],
                labels: ["Comedy", "Action", "SciFi", "Drama", "Horror"],
                dataLabels: {
                    dropShadow: {
                        blur: 3,
                        opacity: 0.8,
                    },
                },
                fill: {
                    type: "pattern",
                    opacity: 1,
                    pattern: {
                        enabled: true,
                        style: [
                            "verticalLines",
                            "squares",
                            "horizontalLines",
                            "circles",
                            "slantedLines",
                        ],
                    },
                },
                states: {
                    hover: {
                        enabled: false,
                    },
                },
                legend: {
                    show: true,
                    position: "bottom",
                    horizontalAlign: "center",
                    verticalAlign: "middle",
                    floating: false,
                    fontSize: "14px",
                    offsetX: 0,
                    offsetY: 7,
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        chart: {
                            height: 240,
                        },
                        legend: {
                            show: false,
                        },
                    },
                }, ],
            },
        };
    },
};
</script>
