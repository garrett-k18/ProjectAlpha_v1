<template>
<div id="chart">
    <apexchart height="380" :options="options" :series="series"></apexchart>
</div>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Series 1",
                    data: [31, 40, 28, 51, 42, 109, 100],
                },
                {
                    name: "Series 2",
                    data: [11, 32, 45, 32, 34, 52, 41],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "area",

                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: 3,
                    curve: "smooth",
                },
                colors: ["#3e60d5", "#6c757d"],

                legend: {
                    offsetY: 5,
                },
                xaxis: {
                    categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
                },
                tooltip: {
                    fixed: {
                        enabled: false,
                        position: "topRight",
                    },
                },
                grid: {
                    row: {
                        colors: ["transparent", "transparent"], // takes an array which will be repeated on columns
                        opacity: 0.2,
                    },
                    borderColor: "#f1f3fa",
                    padding: {
                        bottom: 5,
                    },

                },

            },
        };
    },
};
</script>
