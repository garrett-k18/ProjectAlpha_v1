<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                name: "Series 1",
                data: [20, 100, 40, 30, 50, 80, 33],
            }, ],
            options: {
                chart: {
                    height: 350,
                    type: "radar",
                },

                labels: [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
                plotOptions: {
                    radar: {
                        size: 140,
                    },
                },
                colors: ["#FF4560"],
                markers: {
                    size: 4,
                    colors: ["#fff"],
                    strokeColor: ["#FF4560"],
                    strokeWidth: 2,
                },
                tooltip: {
                    y: {
                        formatter: function (val: number) {
                            return val;
                        },
                    },
                },
                yaxis: {
                    tickAmount: 7,
                    labels: {
                        formatter: function (val: number, i: number) {
                            if (i % 2 === 0) {
                                return val;
                            } else {
                                return "";
                            }
                        },
                    },
                },
            },
        };
    },
};
</script>
