<template>
<Bar id="horizontal-example" :data="data" :options="options" />
</template>

<script lang="ts">
import { hexToRGB } from '../utility';
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
export default {
    components: { Bar },
    data() {
        const colors = ["#727cf5", "#0acf97"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April'],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [12, -19, 14, -15],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], 0.3),
                    borderWidth: 1,
                }, {
                    label: 'Small Radius',
                    data: [-10, 19, -15, -8],
                    backgroundColor: hexToRGB(colors[1], 0.3),
                    borderColor: colors[1],
                    borderWidth: 1,
                }]
            },
            options: {
                indexAxis: 'y',
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
