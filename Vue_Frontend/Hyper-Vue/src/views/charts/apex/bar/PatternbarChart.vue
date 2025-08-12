<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        return {
            series: [{
                name: 'Marine Sprite',
                data: [44, 55, 41, 37, 22, 43, 21]
            }, {
                name: 'Striking Calf',
                data: [53, 32, 33, 52, 13, 43, 32]
            }, {
                name: 'Tank Picture',
                data: [12, 17, 11, 9, 15, 11, 20]
            }, {
                name: 'Bucket Slope',
                data: [9, 7, 5, 8, 6, 9, 4]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'bar',
                    stacked: true,
                    toolbar: {
                        show: false
                    },
                    shadow: {
                        enabled: true,
                        blur: 1,
                        opacity: 0.5
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        barHeight: '60%',

                    },
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    width: 2,
                },
                xaxis: {
                    categories: [2008, 2009, 2010, 2011, 2012, 2013, 2014],
                    axisBorder: {
                        show: false,
                    }
                },
                yaxis: {
                    title: {
                        text: undefined
                    },
                },
                tooltip: {
                    shared: false,
                    y: {
                        formatter: function (val) {
                            return val + "K"
                        }
                    }
                },
                colors: ["#727cf5","#0acf97","#fa5c7c","#39afd1"],
                fill: {
                    type: 'pattern',
                    opacity: 1,
                    pattern: {
                        style: ['circles', 'slantedLines', 'verticalLines', 'horizontalLines'], // string or array of strings

                    }
                },
                states: {
                    hover: {
                        filter: 'none'
                    }
                },
                legend: {
                    position: 'right',
                },
                grid: {
                    borderColor: '#f1f3fa'
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        legend: {
                            show: false
                        },
                    }
                }]
            }
        }
    }
}
</script>
