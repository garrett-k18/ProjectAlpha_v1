<template>
<Line id="point-styling-example" :data="data" :options="options" />
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
                    pointStyle: 'circle',
                    pointRadius: 10,
                    pointHoverRadius: 15
                }, ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },

                },
                scales: {
                    x: {
                        stacked: true,

                        grid: {
                            display: false
                        }
                    },
                    y: {
                        stacked: true,

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
