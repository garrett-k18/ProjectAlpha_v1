<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [70],
            options: {
                chart: {
                    height: 320,
                    type: "radialBar",
                },
                plotOptions: {
                    radialBar: {
                        hollow: {
                            size: "70%",
                        },
                        track: {
                            background: "rgba(170,184,197, 0.2)",
                        },
                    },
                },
                colors: ["#39afd1"],

                labels: ["CRICKET"],
            },
        };
    },
};
</script>
