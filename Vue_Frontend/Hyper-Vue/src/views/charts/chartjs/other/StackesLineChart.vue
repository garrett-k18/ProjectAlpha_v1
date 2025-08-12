<template>
<Line :data="data" :options="options" />
</template>

<script>
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
export default {
    components: { Line },
    data() {
        const colors = ["#727cf5", "#0acf97"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May", "June", "July"],
                datasets: [{
                    label: 'Dataset 1',
                    data: [10, 20, 35, 18, 15, 25, 22],
                    backgroundColor: colors[0],
                    stack: 'combined',
                    type: 'bar'
                }, {
                    label: 'Dataset 2',
                    data: [13, 23, 38, 22, 25, 30, 28],

                    borderColor: colors[1],
                    stack: 'combined'

                }]
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
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        stacked: true,
                        grid: {
                            display: false
                        }
                    }
                }
            },
        }
    },
}
</script>
