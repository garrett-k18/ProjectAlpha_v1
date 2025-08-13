<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [44, 55, 41, 17, 15],
            options: {
                chart: {
                    height: 320,
                    type: "pie",
                },

                labels: ["Series 1", "Series 2", "Series 3", "Series 4", "Series 5"],
                colors: ["#727cf5", "#6c757d", "#0acf97", "#fa5c7c", "#e3eaef"],
                legend: {
                    show: true,
                    position: "bottom",
                    horizontalAlign: "center",
                    verticalAlign: "middle",
                    floating: false,
                    fontSize: "14px",
                    offsetX: 0,
                    offsetY: 7,
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        chart: {
                            height: 240,
                        },
                        legend: {
                            show: false,
                        },
                    },
                }, ],
            },
        };
    },
};
</script>
