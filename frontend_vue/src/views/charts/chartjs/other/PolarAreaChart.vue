<template>
<PolarArea :data="data" :options="options" />
</template>

<script>
import { Chart as ChartJS, RadialLinearScale, ArcElement, Tooltip, Legend } from 'chart.js'
import { PolarArea } from 'vue-chartjs'

ChartJS.register(RadialLinearScale, ArcElement, Tooltip, Legend)
export default {
    components: { PolarArea },
    data() {
        const colors = ["#727cf5", "#fa5c7c", "#0acf97", "#ebeff2", " #f56f36"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May"],
                datasets: [{
                    label: 'Dataset 1',
                    data: [12, 19, 14, 15, 20],
                    backgroundColor: colors,
                }, ]
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
                    r: {
                        display: false
                    }
                }
            },
        }
    },
}
</script>
