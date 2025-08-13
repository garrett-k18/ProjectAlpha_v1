<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        const colors = ["#0acf97","#fa5c7c"];
        return {
            series: [{
                name: 'Actual',
                data: [{
                        x: '2017',
                        y: 12,
                        goals: [{
                            name: 'Expected',
                            value: 14,
                            strokeWidth: 2,
                            strokeDashArray: 2,
                            strokeColor: colors[1]
                        }]
                    },
                    {
                        x: '2018',
                        y: 44,
                        goals: [{
                            name: 'Expected',
                            value: 54,
                            strokeWidth: 5,
                            strokeHeight: 10,
                            strokeColor: colors[1]
                        }]
                    },
                    {
                        x: '2019',
                        y: 54,
                        goals: [{
                            name: 'Expected',
                            value: 52,
                            strokeWidth: 10,
                            strokeHeight: 0,
                            strokeLineCap: 'round',
                            strokeColor: colors[1]
                        }]
                    },
                    {
                        x: '2020',
                        y: 66,
                        goals: [{
                            name: 'Expected',
                            value: 61,
                            strokeWidth: 10,
                            strokeHeight: 0,
                            strokeLineCap: 'round',
                            strokeColor: colors[1]
                        }]
                    },
                    {
                        x: '2021',
                        y: 81,
                        goals: [{
                            name: 'Expected',
                            value: 66,
                            strokeWidth: 10,
                            strokeHeight: 0,
                            strokeLineCap: 'round',
                            strokeColor: colors[1]
                        }]
                    },
                    {
                        x: '2022',
                        y: 67,
                        goals: [{
                            name: 'Expected',
                            value: 70,
                            strokeWidth: 5,
                            strokeHeight: 10,
                            strokeColor: colors[1]
                        }]
                    }
                ]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'bar'
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                    }
                },
                colors: colors,
                dataLabels: {
                    dataLabels: {
                        formatter: function (val, opt) {
                            var goals =
                                opt.w.config.series[opt.seriesIndex].data[opt.dataPointIndex]
                                .goals

                            // if (goals && goals.length) {
                            //   return `${val} / ${goals[0].value}`
                            // }
                            return val
                        }
                    },
                },
                legend: {
                    show: true,
                    showForSingleSeries: true,
                    customLegendItems: ['Actual', 'Expected'],
                    markers: {
                        fillColors: colors
                    }
                },
                xaxis: {
                    axisBorder: {
                        show: false,
                    }
                }
            }
        }
    }
}
</script>
