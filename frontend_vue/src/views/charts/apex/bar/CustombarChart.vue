<template>
<apexchart height="450" :series="series" :options="options"></apexchart>
</template>

<script>
export default {
    data: function () {
        return {
            series: [{
                data: [400, 430, 448, 470, 540, 580, 690, 1100, 1200, 1380]
            }],
            options: {
                chart: {
                    height: 450,
                    type: 'bar'
                },
                plotOptions: {
                    bar: {
                        barHeight: '100%',
                        distributed: true,
                        horizontal: true,
                        dataLabels: {
                            position: 'bottom'
                        },
                    }
                },
                colors: ["#727cf5","#0acf97","#fa5c7c","#6c757d","#39afd1","#2b908f","#ffbc00","#90ee7e","#f48024","#212730"],
                dataLabels: {
                    enabled: true,
                    textAnchor: 'start',
                    style: {
                        colors: ['#fff']
                    },
                    formatter: function (val, opt) {
                        return opt.w.globals.labels[opt.dataPointIndex] + ":  " + val
                    },
                    offsetX: 0,
                    dropShadow: {
                        enabled: false
                    }
                },

                stroke: {
                    width: 0,
                    colors: ['#fff']
                },
                xaxis: {
                    categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan', 'United States', 'China', 'India'],
                    axisBorder: {
                        show: false,
                    }
                },
                yaxis: {
                    labels: {
                        show: false
                    }
                },
                grid: {
                    borderColor: '#f1f3fa'
                },

                tooltip: {
                    theme: 'dark',
                    x: {
                        show: false
                    },
                    y: {
                        title: {
                            formatter: function () {
                                return ''
                            }
                        }
                    }
                }
            }
        }
    }
}
</script>
