<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [76, 67, 61, 90],
            options: {
                chart: {
                    height: 380,
                    type: "radialBar",
                },
                plotOptions: {
                    radialBar: {
                        offsetY: -30,
                        startAngle: 0,
                        endAngle: 270,
                        hollow: {
                            margin: 5,
                            size: "30%",
                            background: "transparent",
                            image: undefined,
                        },
                        track: {
                            background: "rgba(170,184,197, 0.2)",
                        },
                        dataLabels: {
                            name: {
                                show: false,
                            },
                            value: {
                                show: false,
                            },
                        },
                    },
                },
                colors: ["#0acf97", "#727cf5", "#fa5c7c", "#ffbc00"],

                labels: ["Vimeo", "Messenger", "Facebook", "LinkedIn"],
                legend: {
                    show: true,
                    floating: true,
                    fontSize: "13px",
                    position: "left",
                    offsetX: 10,
                    offsetY: 10,
                    labels: {
                        useSeriesColors: true,
                    },
                    markers: {
                        size: 0,
                    },
                    formatter: function (seriesName: string, opts: any) {
                        return seriesName + ":  " + opts.w.globals.series[opts.seriesIndex];
                    },
                    itemMargin: {
                        horizontal: 1,
                    },
                },
                responsive: [{
                    breakpoint: 480,
                    options: {
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
