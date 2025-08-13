<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                name: 'Team A',
                type: 'area',
                data: [44, 55, 31, 47, 31, 43, 26, 41, 31, 47, 33]
            }, {
                name: 'Team B',
                type: 'line',
                data: [55, 69, 45, 61, 43, 54, 37, 52, 44, 61, 43]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'line',
                    toolbar: {
                        show: false
                    }
                },
                stroke: {
                    curve: 'smooth',
                    width: 2
                },
                fill: {
                    type: 'solid',
                    opacity: [0.35, 1],
                },
                labels: ['Dec 01', 'Dec 02', 'Dec 03', 'Dec 04', 'Dec 05', 'Dec 06', 'Dec 07', 'Dec 08', 'Dec 09 ', 'Dec 10', 'Dec 11'],
                markers: {
                    size: 0
                },
                legend: {
                    offsetY: 7,
                },
                colors: ["#0acf97", "#fa5c7c"],
                yaxis: [{
                        title: {
                            text: 'Series A',
                        },
                    },
                    {
                        opposite: true,
                        title: {
                            text: 'Series B',
                        },
                    },
                ],
                tooltip: {
                    shared: true,
                    intersect: false,
                    y: {
                        formatter: function (y) {
                            if (typeof y !== "undefined") {
                                return y.toFixed(0) + " points";
                            }
                            return y;

                        }
                    }
                },
                grid: {
                    borderColor: '#f1f3fa',
                    padding: {
                        bottom: 5
                    }
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        yaxis: {
                            show: false
                        },
                        legend: {
                            show: false
                        }
                    }
                }]
            }
        }
    },
}
</script>
