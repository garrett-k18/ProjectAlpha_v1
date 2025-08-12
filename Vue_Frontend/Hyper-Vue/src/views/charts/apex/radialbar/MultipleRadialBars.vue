<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [44, 55, 67, 83],
            options: {
                chart: {
                    height: 320,
                    type: "radialBar",
                },
                plotOptions: {
                    circle: {
                        dataLabels: {
                            showOn: "hover",
                        },
                    },
                    radialBar: {
                        track: {
                            background: "rgba(170,184,197, 0.2)",
                        },
                    },
                },
                colors: ["#6c757d", "#ffbc00", "#727cf5", "#0acf97"],
                labels: ["Apples", "Oranges", "Bananas", "Berries"],
                responsive: [{
                    breakpoint: 380,
                    options: {
                        chart: {
                            height: 260,
                        },
                    },
                }, ],
            },
        };
    },
};
</script>
