<template>
<apexchart height="396" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        const colors = ["#727cf5","#0acf97","#fa5c7c"];
        return {
            series: [{
                name: 'Net Profit',
                data: [44, 55, 57, 56, 61, 58, 63, 60, 66]
            }, {
                name: 'Revenue',
                data: [76, 85, 101, 98, 87, 105, 91, 114, 94]
            }, {
                name: 'Free Cash Flow',
                data: [35, 41, 36, 26, 45, 48, 52, 53, 41]
            }],
            options: {
                chart: {
                    height: 396,
                    type: 'bar',
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        endingShape: 'rounded',
                        columnWidth: '55%',
                    },
                },
                dataLabels: {
                    enabled: false
                },
                stroke: {
                    show: true,
                    width: 2,
                    colors: ['transparent']
                },
                colors: colors,
                xaxis: {
                    categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                },
                legend: {
                    offsetY: 7,
                },
                yaxis: {
                    title: {
                        text: '$ (thousands)'
                    }
                },
                fill: {
                    opacity: 1
                },
                grid: {
                    row: {
                        colors: ['transparent', 'transparent'], // takes an array which will be repeated on columns
                        opacity: 0.2
                    },
                    borderColor: '#f1f3fa',
                    padding: {
                        bottom: 5
                    }
                },
                tooltip: {
                    y: {
                        formatter: function (val) {
                            return "$ " + val + " thousands"
                        }
                    }
                }
            }
        }
    }
}
</script>
