<template>
<apexchart height="380" :series="series" :options="options"></apexchart>
</template>

<script>
export default {
    data: function () {
        return {
            series: [{
                name: 'Series 1',
                data: [44, 55, 41, 64, 22, 43, 21]
            }, {
                name: 'Series 2',
                data: [53, 32, 33, 52, 13, 44, 32]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'bar',
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        dataLabels: {
                            position: 'top',
                        },
                    }
                },
                dataLabels: {
                    enabled: true,
                    offsetX: -6,
                    style: {
                        fontSize: '12px',
                        colors: ['#fff']
                    }
                },
                colors: ["#fa5c7c","#6c757d"],
                stroke: {
                    show: true,
                    width: 1,
                    colors: ['transparent']
                },
                xaxis: {
                    categories: [2001, 2002, 2003, 2004, 2005, 2006, 2007],
                    axisBorder: {
                        show: false,
                    }
                },
                legend: {
                    offsetY: 5,
                },
                states: {
                    hover: {
                        filter: 'none'
                    }
                },
                grid: {
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
