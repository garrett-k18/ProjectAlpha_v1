<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Product A",
                    data: [{
                            x: "Team A",
                            y: [1, 5],
                        },
                        {
                            x: "Team B",
                            y: [4, 6],
                        },
                        {
                            x: "Team C",
                            y: [5, 8],
                        },
                        {
                            x: "Team D",
                            y: [3, 11],
                        },
                    ],
                },
                {
                    name: "Product B",
                    data: [{
                            x: "Team A",
                            y: [2, 6],
                        },
                        {
                            x: "Team B",
                            y: [1, 3],
                        },
                        {
                            x: "Team C",
                            y: [7, 8],
                        },
                        {
                            x: "Team D",
                            y: [5, 9],
                        },
                    ],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "rangeBar",
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                    },
                },
                dataLabels: {
                    enabled: true,
                },
                legend: {
                    offsetY: 7,
                },
                colors: ["#0acf97", "#39afd1"],
            },
        };
    },
};
</script>
