<template>
<Line id="line-segment-example" :data="data" :options="options" />
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
                labels: ['Jan', 'Feb', 'March', 'April', "May", "June", "July"],
                datasets: [{
                    label: 'Dataset 1',
                    data: [65, 59, NaN, 48, 56, 57, 40],
                    borderColor: colors[0],
                    spanGaps: true,
                    // segment: {
                    //     borderColor: function (ctx) { return this.skipped(ctx, 'rgb(0,0,0,0.2)') || this.down(ctx, 'rgb(192,75,75)') },
                    //     borderDash: function (ctx) { return this.skipped(ctx, [6, 6]) },
                    // },

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
