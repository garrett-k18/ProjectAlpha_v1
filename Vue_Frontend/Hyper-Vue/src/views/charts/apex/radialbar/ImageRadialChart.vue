<template>
<apexchart height="360" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
import small2 from "@/assets/images/small/small-2.jpg"
export default {
    data() {
        return {
            series: [70],
            options: {
                chart: {
                    height: 360,
                    type: "radialBar",
                },
                fill: {
                    type: "image",
                    image: {
                        src: [small2],
                    },
                },
                plotOptions: {
                    radialBar: {
                        hollow: {
                            size: "70%",
                        },
                    },
                },
                stroke: {
                    lineCap: "round",
                },
                labels: ["Volatility"],
                responsive: [{
                    breakpoint: 380,
                    options: {
                        chart: {
                            height: 280,
                        },
                    },
                }, ],
            },
        };
    },
};
</script>
