<template>
<Line id="interpolation-example" :options="options" :data="data" />
</template>

<script lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default {
    components: { Line },
    data() {
        const colors = ["#727cf5","#0acf97"]
        const datapoints = [0, 20, 20, 60, 60, 120, NaN, 180, 120, 125, 105, 110, 170];
        return {
            data: {
                labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                datasets: [{
                    label: 'Fully Rounded',
                    data: datapoints,
                    borderColor: colors[0],
                    fill: false,
                    cubicInterpolationMode: 'monotone',
                    tension: 0.4
                }, {
                    label: 'Small Radius',
                    data: datapoints,
                    borderColor: colors[1],
                    fill: false,
                    tension: 0.4
                }, {
                    label: 'Small Radius',
                    data: datapoints,
                    borderColor: colors[2],
                    fill: false,
                }, ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: false,

                        position: 'top',
                    },

                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        suggestedMin: -10,
                        suggestedMax: 200
                    },
                }
            },
        }
    },
}
</script>
