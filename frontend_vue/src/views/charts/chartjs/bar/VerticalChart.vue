<template>
<Bar id="vertical-example" :data="data" :options="options" />
</template>

<script lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
export default {
    components: { Bar },
    data() {
        const colors = ["#727cf5", "#0acf97"]
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April'],
                datasets: [{
                    label: 'Dataset 1',
                    data: [12, -19, 14, -15],
                    backgroundColor: colors[0],

                }, {
                    label: 'Dataset 2',
                    data: [-10, 19, -15, -8],
                    backgroundColor: colors[1],

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
