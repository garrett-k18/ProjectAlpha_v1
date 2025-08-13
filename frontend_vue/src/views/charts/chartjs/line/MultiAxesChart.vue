<template>
<Line id="multi-axes-example" :data="data" :options="options"/>
</template>

<script lang="ts">
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

import { hexToRGB } from '../utility';
export default {
    components: { Line },
    data() {
        const colors = ["#3e60d5", "#47ad77"]
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May", "June", "July"],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [12, -19, 14, -15, 18, -14, -7],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], 0.3),
                    borderWidth: 1.5,
                    yAxisID: 'y',

                }, {
                    label: 'Small Radius',
                    data: [-10, 19, -15, -8, -17, 12, 8],
                    backgroundColor: hexToRGB(colors[1], 0.3),
                    borderColor: colors[1],
                    borderWidth: 1.5,
                    yAxisID: 'y1',

                }]
            },
            options: {
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,

                        position: 'top',
                    },

                },
                tension: 0.2,
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            display: false
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false, // only want the grid lines for one axis to show up
                        },
                    },
                }
            },
        }
    },
}
</script>
