<template>
<Line id="stepped-example" :data="data" :options="options" />
</template>

<script lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)
export default {
    components: { Line },
    data() {
        const colors = ["#727cf5", "#0acf97"]
        return {
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6'],
                datasets: [{
                    label: 'Dataset 1',
                    data: [12, -19, 14, -15, 14, -8],
                    borderColor: colors[0],
                    fill: false,
                    spanGaps: true,

                }, ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    axis: 'x'
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
                        }
                    },
                }
            },
        }
    },
}
</script>
