<template>
<Doughnut :data="data" :options="options" />
</template>

<script>
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)
import { Doughnut } from 'vue-chartjs'
export default {
    components: { Doughnut },
    data() {
        const colors = ["#727cf5", "#fa5c7c", "#0acf97", "#ebeff2"];
        return {
            data: {
                labels: ["Direct", "Affilliate", "Sponsored", "E-mail"],
                datasets: [{
                    data: [300, 135, 48, 154],
                    backgroundColor: colors,
                    borderColor: "transparent",
                    borderWidth: "3",
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutoutPercentage: 60,
                plugins: {
                    legend: {
                        display: false,

                        position: 'top',
                    },

                },
            },
        }
    },
}
</script>
