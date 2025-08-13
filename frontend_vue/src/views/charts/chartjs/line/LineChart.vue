<template>
<Line id="line-example" :data="data" :options="options" />
</template>

<script lang="ts">
import { hexToRGB } from '../utility'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)
export default {
    components: { Line },
    data() {
        const colors = ["#727cf5", "#0acf97"]
        return {
            data: {
                labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [32, 42, 42, 62, 52, 75, 62],
                    borderColor: colors[0],
                    fill: true,
                    backgroundColor: hexToRGB(colors[0], 0.3),

                }, {
                    label: 'Small Radius',
                    data: [42, 58, 66, 93, 82, 105, 92],
                    fill: true,
                    backgroundColor: 'transparent',
                    borderColor: colors[1],
                    borderDash: [5, 5],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false,

                        position: 'top',
                    },

                },
                tension: 0.3,
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    },
                }
            },
        }
    },
}
</script>
