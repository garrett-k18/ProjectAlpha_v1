<template>
<apexchart height="380" :series="series" :options="options"></apexchart>
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
                    height: 380,
                    type: 'bar',
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                    }
                },
                dataLabels: {
                    enabled: false
                },

                colors: ["#39afd1"],
                xaxis: {
                    categories: ['South Korea', 'Canada', 'United Kingdom', 'Netherlands', 'Italy', 'France', 'Japan', 'United States', 'China', 'Germany'],
                    axisBorder: {
                        show: false,
                    }
                },
                states: {
                    hover: {
                        filter: 'none'
                    }
                },
                grid: {
                    borderColor: '#f1f3fa'
                }
            }
        }
    }
}
</script>
