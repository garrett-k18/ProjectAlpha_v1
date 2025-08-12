<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [25, 15, 44, 55, 41, 17],
            options: {
                chart: {
                    height: 320,
                    type: "pie",
                },
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
                theme: {
                    monochrome: {
                        enabled: true,
                    },
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
