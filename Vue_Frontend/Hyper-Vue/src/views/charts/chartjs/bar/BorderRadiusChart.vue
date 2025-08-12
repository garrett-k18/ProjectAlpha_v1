<template>
<Bar id="radar-example" :options="options" :data="data" />
</template>

<script lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

import { hexToRGB } from '../utility';

export default {
    components: { Bar },
    data() {
        const colors = ["#727cf5", "#0acf97"]
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', 'May', 'June'],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [12, -19, 14, -15, 12, -14],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], .3),
                    borderWidth: 2,
                    borderRadius: Number.MAX_VALUE,
                    borderSkipped: false,
                }, {
                    label: 'Small Radius',
                    data: [-10, 19, -15, -8, 12, -7],
                    backgroundColor: hexToRGB(colors[1], .3),
                    borderColor: colors[1],
                    borderWidth: 2,
                    borderRadius: 5,
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
