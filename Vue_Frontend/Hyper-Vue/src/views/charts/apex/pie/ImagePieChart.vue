<template>
<apexchart height="320" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
import small1 from "@/assets/images/small/small-1.jpg";
import small2 from "@/assets/images/small/small-2.jpg";
import small3 from "@/assets/images/small/small-3.jpg";
import small4 from "@/assets/images/small/small-4.jpg";

export default {
    data() {
        return {
            series: [44, 33, 54, 45],
            options: {
                chart: {
                    height: 320,
                    type: "pie",
                },
                labels: ["Series 1", "Series 2", "Series 3", "Series 4"],
                colors: ["#39afd1", "#ffbc00", "#727cf5", "#0acf97"],
                fill: {
                    type: "image",
                    opacity: 0.85,
                    image: {
                        src: [small1, small2, small3, small4],
                        width: 25,
                        imagedHeight: 25,
                    },
                },
                stroke: {
                    width: 4,
                },
                dataLabels: {
                    enabled: false,
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
