<template>
<Radar :data="data" :options="options" />
</template>

<script>
import { hexToRGB } from '../utility'
import { Radar } from 'vue-chartjs'
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Title, Tooltip, Legend)
export default {
    components: { Radar },
    data() {
        const colors = ["#727cf5", "#0acf97"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May", "June"],
                datasets: [{
                    label: 'Dataset 1',
                    data: [12, 29, 39, 22, 28, 34],
                    borderColor: colors[0],
                    backgroundColor: hexToRGB(colors[0], .3),

                }, {
                    label: 'Dataset 2',
                    data: [10, 19, 15, 28, 34, 39],
                    borderColor: colors[1],
                    backgroundColor: hexToRGB(colors[1], .3),

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
            },
        }
    },
}
</script>
