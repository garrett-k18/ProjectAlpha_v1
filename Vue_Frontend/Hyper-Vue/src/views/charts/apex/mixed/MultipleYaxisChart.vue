<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#727cf5", "#39afd1", "#fa5c7c"]
        return {
            series: [{
                    name: "Income",
                    type: "column",
                    data: [1.4, 2, 2.5, 1.5, 2.5, 2.8, 3.8, 4.6],
                },
                {
                    name: "Cashflow",
                    type: "column",
                    data: [1.1, 3, 3.1, 4, 4.1, 4.9, 6.5, 8.5],
                },
                {
                    name: "Revenue",
                    type: "line",
                    data: [20, 29, 37, 36, 44, 45, 50, 58],
                },
            ],
            options: {
                chart: {
                    height: 380,
                    type: "line",
                    stacked: false,
                    toolbar: {
                        show: false,
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: [0, 0, 3],
                },

                colors: colors,
                xaxis: {
                    categories: [2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                },
                yaxis: [{
                        axisTicks: {
                            show: true,
                        },
                        axisBorder: {
                            show: true,
                            color: colors[0],
                        },
                        labels: {
                            style: {
                                color: colors[0],
                            },
                        },
                        title: {
                            text: "Income (thousand crores)",
                        },
                    },

                    {
                        axisTicks: {
                            show: true,
                        },
                        axisBorder: {
                            show: true,
                            color: colors[1],
                        },
                        labels: {
                            style: {
                                color: colors[1],
                            },
                            offsetX: 10,
                        },
                        title: {
                            text: "Operating Cashflow (thousand crores)",
                        },
                    },
                    {
                        opposite: true,
                        axisTicks: {
                            show: true,
                        },
                        axisBorder: {
                            show: true,
                            color: colors[2],
                        },
                        labels: {
                            style: {
                                color: colors[2],
                            },
                        },
                        title: {
                            text: "Revenue (thousand crores)",
                        },
                    },
                ],
                tooltip: {
                    followCursor: true,
                    y: {
                        formatter: function (y: number) {
                            if (typeof y !== "undefined") {
                                return y + " thousand crores";
                            }
                            return y;
                        },
                    },
                },
                grid: {
                    borderColor: "#f1f3fa",
                    padding: {
                        bottom: 5,
                    },
                },
                legend: {
                    offsetY: 7,
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        yaxis: {
                            show: false,
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
