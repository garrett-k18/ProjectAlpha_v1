<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        let lastDate = 0;
        // let data: { x: number; y: number }[] = [];
        let dataPointsLength = 10;
        return {
            lastDate,
            // data,
            series: [{
                data: [],
            }, ],
            options: {
                chart: {
                    height: 350,
                    type: "line",
                    animations: {
                        enabled: true,
                        easing: "linear",
                        dynamicAnimation: {
                            speed: 2000,
                        },
                    },
                    toolbar: {
                        show: false,
                    },
                    zoom: {
                        enabled: false,
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    curve: "smooth",
                    width: [3],
                },
                colors: ["#39afd1"],

                markers: {
                    size: 0,
                },
                xaxis: {
                    type: "datetime",
                    range: 777600000,
                },
                yaxis: {
                    max: 100,
                },
                legend: {
                    show: false,
                },
                grid: {
                    borderColor: "#f1f3fa",
                },
            },
        };
    },
    mounted() {
        this.getDayWiseTimeSeries(new Date("11 Feb 2017 GMT").getTime(), 10, {
            min: 10,
            max: 90,
        });

        //     const self = this
        window.setInterval(() => {
            this.getNewSeries(this.lastDate, {
                min: 10,
                max: 90
            });
        }, 2000);

        window.setInterval(() => {
            this.series[0].data = this.resetData();
        }, 60000);

    },
    methods: {
        getDayWiseTimeSeries(
            baseval: number,
            count: number,
            yrange: { max: number;min: number }
        ) {
            let i = 0;
            while (i < count) {
                let x = baseval;
                let y =
                    Math.floor(Math.random() * (yrange.max - yrange.min + 1)) +
                    yrange.min;

                this.series[0].data.push({
                    x: x,
                    y: y,
                });
                this.lastDate = baseval;
                baseval += 86400000;
                i++;
            }
        },

        getNewSeries(baseval: number, yrange: { max: number;min: number }) {
            let newDate = baseval + 86400000;
            this.lastDate = newDate;
            this.series[0].data.push({
                x: newDate,
                y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) +
                    yrange.min,
            });
        },
        resetData() {
            return this.series[0].data.slice(this.series[0].data.length - 10, this.series[0].data.length);
        },

    },
};
</script>
