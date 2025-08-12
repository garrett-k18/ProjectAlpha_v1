<template>
<Scatter :data="data" :options="options" />
</template>

<script>
import { hexToRGB } from '../utility'
import { Chart as ChartJS, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js'
import { Scatter } from 'vue-chartjs'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)
export default {
    components: { Scatter },
    data() {
        const colors = ["#727cf5", "#0acf97"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May", "June", "July"],
                datasets: [{
                    label: 'Dataset 1',
                    data: [{ x: 10, y: 50, }, { x: 50, y: 10, }, { x: 15, y: 15, }, { x: 20, y: 45, }, { x: 25, y: 18, }, { x: 34, y: 38, }, ],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], .3),

                }, {
                    label: 'Dataset 2',
                    data: [{ x: 15, y: 45, }, { x: 40, y: 20, }, { x: 30, y: 5, }, { x: 35, y: 25, }, { x: 18, y: 25, }, { x: 40, y: 8, }, ],
                    borderColor: colors[1],
                    backgroundColor: hexToRGB(colors[1], .3),

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
