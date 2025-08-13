<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Peter",
                    data: [5, 5, 10, 8, 7, 5, 4, null, null, null, 10, 10, 7, 8, 6, 9],
                },
                {
                    name: "Johnny",
                    data: [
                        10,
                        15,
                        null,
                        12,
                        null,
                        10,
                        12,
                        15,
                        null,
                        null,
                        12,
                        null,
                        14,
                        null,
                        null,
                        null,
                    ],
                },
                {
                    name: "David",
                    data: [
                        null,
                        null,
                        null,
                        null,
                        3,
                        4,
                        1,
                        3,
                        4,
                        6,
                        7,
                        9,
                        5,
                        null,
                        null,
                        null,
                    ],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "line",
                    zoom: {
                        enabled: false,
                    },
                    animations: {
                        enabled: false,
                    },
                },
                stroke: {
                    width: [5, 5, 4],
                    curve: "straight",
                },

                colors: ["#ffbc00", "#0acf97", "#39afd1"],
                labels: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
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
                legend: {
                    offsetY: 7,
                },
            },
        };
    },
};
</script>
