<template>
<Pie :data="data" :options="options" />
</template>

<script>
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)
export default {
    components: { Pie },
    data() {
        const colors = ["#727cf5", "#fa5c7c", "#0acf97", "#ebeff2", " #f56f36"];
        return {
            data: {
                labels: ['Jan', 'Feb', 'March', 'April', "May"],
                datasets: [{
                    label: 'Fully Rounded',
                    data: [12, 19, 14, 15, 40],
                    backgroundColor: colors,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },

                }
            },
        }
    },

}
</script>
