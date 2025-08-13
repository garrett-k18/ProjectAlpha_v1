<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                name: "Series 1",
                data: [80, 50, 30, 40, 100, 20],
            }, ],
            options: {
                chart: {
                    height: 350,
                    type: "radar",
                },

                colors: ["#727cf5"],
                labels: ["January", "February", "March", "April", "May", "June"],
            },
        };
    },
};
</script>
