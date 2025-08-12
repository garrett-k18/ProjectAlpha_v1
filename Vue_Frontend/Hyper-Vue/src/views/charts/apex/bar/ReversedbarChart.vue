<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        const colors = ["#727cf5", "#0acf97"];
        return {
            series: [{
                data: [400, 430, 448, 470, 540, 580, 690]
            }],
            options: {
                chart: {
                    type: 'bar',
                    height: 380
                },
                annotations: {
                    xaxis: [{
                        x: 500,
                        borderColor: colors[1],
                        label: {
                            borderColor: colors[1],
                            style: {
                                color: '#fff',
                                background: colors[1],
                            },
                            text: 'X annotation',
                        }
                    }],
                    yaxis: [{
                        y: 'July',
                        y2: 'September',
                        label: {
                            text: 'Y annotation'
                        }
                    }]
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                    }
                },
                dataLabels: {
                    enabled: true
                },
                xaxis: {
                    categories: ['June', 'July', 'August', 'September', 'October', 'November', 'December'],
                    axisBorder: {
                        show: false,
                    }
                },
                colors: ["#727cf5", "#0acf97"],
                grid: {
                    xaxis: {
                        lines: {
                            show: true
                        }
                    }
                },
                yaxis: {
                    reversed: true,
                    axisTicks: {
                        show: true
                    }
                }
            }
        }
    }
}
</script>
