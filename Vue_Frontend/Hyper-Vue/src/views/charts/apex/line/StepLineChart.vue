<template>
<apexchart height="344" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                data: [34, 44, 54, 21, 12, 43, 33, 23, 66, 66, 58],
            }, ],
            options: {
                chart: {
                    type: "line",
                    height: 344,
                },
                stroke: {
                    curve: "stepline",
                },
                dataLabels: {
                    enabled: false,
                },
                colors: ["#0acf97"],
                title: {
                    text: "Stepline Chart",
                    align: "left",
                },
                markers: {
                    hover: {
                        sizeOffset: 4,
                    },
                },
            },
        };
    },
};
</script>
