<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Session Duration",
                    data: [45, 52, 38, 24, 33, 26, 21, 20, 6, 8, 15, 10],
                },
                {
                    name: "Page Views",
                    data: [35, 41, 62, 42, 13, 18, 29, 37, 36, 51, 32, 35],
                },
                {
                    name: "Total Visits",
                    data: [87, 57, 74, 99, 75, 38, 62, 47, 82, 56, 45, 47],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "line",
                    zoom: {
                        enabled: false,
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: [3, 5, 3],
                    curve: "straight",
                    dashArray: [0, 8, 5],
                },

                markers: {
                    size: 0,
                    style: "hollow", // full, hollow, inverted
                },
                xaxis: {
                    categories: [
                        "01 Jan",
                        "02 Jan",
                        "03 Jan",
                        "04 Jan",
                        "05 Jan",
                        "06 Jan",
                        "07 Jan",
                        "08 Jan",
                        "09 Jan",
                        "10 Jan",
                        "11 Jan",
                        "12 Jan",
                    ],
                },
                colors: ["#6c757d", "#0acf97", "#39afd1"],
                tooltip: {
                    y: {
                        title: {
                            formatter: function (val: string) {
                                if (val === "Session Duration") return val + " (mins)";
                                else if (val === "Page Views") return val + " per session";
                                return val;
                            },
                        },
                    },
                },
                grid: {
                    borderColor: "#f1f3fa",
                },
                legend: {
                    offsetY: 7,
                },
            },
        };
    },
};
</script>
