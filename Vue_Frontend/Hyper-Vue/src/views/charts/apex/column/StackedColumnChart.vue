<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        const colors = ["#39afd1", "#ffbc00", "#e3eaef"];
        return {
            series: [{
                name: 'Product A',
                data: [44, 55, 41, 67, 22, 43, 21, 49]
            }, {
                name: 'Product B',
                data: [13, 23, 20, 8, 13, 27, 33, 12]
            }, {
                name: 'Product C',
                data: [11, 17, 15, 15, 21, 14, 15, 13]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'bar',
                    stacked: true,
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: '50%',
                    },
                },
                xaxis: {
                    categories: ['2011 Q1', '2011 Q2', '2011 Q3', '2011 Q4', '2012 Q1', '2012 Q2', '2012 Q3', '2012 Q4'],
                },
                colors: colors,
                fill: {
                    opacity: 1
                },
                legend: {
                    offsetY: 7,
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
                }
            }
        }
    }
}
</script>
