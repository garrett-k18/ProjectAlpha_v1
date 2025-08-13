<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Website Blog",
                    type: "column",
                    data: [440, 505, 414, 671, 227, 413, 201, 352, 752, 320, 257, 160],
                },
                {
                    name: "Social Media",
                    type: "line",
                    data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "line",
                    toolbar: {
                        show: false,
                    },
                },
                stroke: {
                    width: [0, 4],
                },
                labels: [
                    "01 Jan 2001",
                    "02 Jan 2001",
                    "03 Jan 2001",
                    "04 Jan 2001",
                    "05 Jan 2001",
                    "06 Jan 2001",
                    "07 Jan 2001",
                    "08 Jan 2001",
                    "09 Jan 2001",
                    "10 Jan 2001",
                    "11 Jan 2001",
                    "12 Jan 2001",
                ],
                xaxis: {
                    type: "datetime",
                },
                colors: ["#727cf5","#0acf97"],
                yaxis: [{
                        title: {
                            text: "Website Blog",
                        },
                    },
                    {
                        opposite: true,
                        title: {
                            text: "Social Media",
                        },
                    },
                ],
                legend: {
                    offsetY: 7,
                },
                grid: {
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
