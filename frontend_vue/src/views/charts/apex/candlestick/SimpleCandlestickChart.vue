<template>
<apexchart height="400" :options="options" :series="series"></apexchart>
</template>

<script>
import { seriesData } from './data'
export default {
    data: function () {
        const colors = ["#47ad77", "#fa5c7c"];
        return {
            series: [{
                data: seriesData
            }],
            options: {
                chart: {
                    height: 400,
                    type: 'candlestick'
                },
                plotOptions: {
                    candlestick: {
                        colors: {
                            upward: colors[0],
                            downward: colors[1]
                        }
                    }
                },
                stroke: {
                    show: true,
                    colors: '#f1f3fa',
                    width: 1
                },
                xaxis: {
                    type: 'datetime'
                },
                grid: {
                    borderColor: '#f1f3fa'
                }
            }
        }
    }
}
</script>
