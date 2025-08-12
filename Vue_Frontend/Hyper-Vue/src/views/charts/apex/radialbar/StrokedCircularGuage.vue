<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [67],
            options: {
                chart: {
                    height: 380,
                    type: "radialBar",
                },
                plotOptions: {
                    radialBar: {
                        startAngle: -135,
                        endAngle: 135,
                        dataLabels: {
                            name: {
                                fontSize: "16px",
                                color: undefined,
                                offsetY: 120,
                            },
                            value: {
                                offsetY: 76,
                                fontSize: "22px",
                                color: undefined,
                                formatter: function (val: number) {
                                    return val + "%";
                                },
                            },
                        },
                        track: {
                            background: "rgba(170,184,197, 0.2)",
                            margin: 0,
                        },
                    },
                },
                fill: {
                    gradient: {
                        enabled: true,
                        shade: "dark",
                        shadeIntensity: 0.2,
                        inverseColors: false,
                        opacityFrom: 1,
                        opacityTo: 1,
                        stops: [0, 50, 65, 91],
                    },
                },
                stroke: {
                    dashArray: 4,
                },
                colors: ["#727cf5"],

                labels: ["Median Ratio"],
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
