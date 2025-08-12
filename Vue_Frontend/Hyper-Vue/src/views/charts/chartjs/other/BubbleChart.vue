<template>
<Bubble :data="data" :options="options" />
</template>

<script>
import { Chart as ChartJS, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)
import { Bubble } from 'vue-chartjs'
import { hexToRGB } from '../utility'
export default {
    components: { Bubble, hexToRGB },
    data() {
        const colors = ["#727cf5", "#0acf97"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', 'May', 'June'],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [{ x: 10, y: 20, r: 5 }, { x: 20, y: 10, r: 5 }, { x: 15, y: 15, r: 5 }, ],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], .3),
                    borderWidth: 2,
                    borderSkipped: false,
                }, {
                    label: 'Small Radius',
                    data: [{ x: 12, y: 22 }, { x: 22, y: 20 }, { x: 5, y: 15 }, ],
                    backgroundColor: hexToRGB(colors[1], .3),
                    borderColor: colors[1],
                    borderWidth: 2,
                    borderSkipped: false,
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
