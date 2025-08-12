<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
<div class="text-center mt-2">
    <b-button variant="primary" size="sm" @click="update()">Update</b-button>
</div>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Series 1",
                    data: [80, 50, 30, 40, 100, 20],
                },
                {
                    name: "Series 2",
                    data: [20, 30, 40, 80, 20, 80],
                },
                {
                    name: "Series 3",
                    data: [44, 76, 78, 13, 43, 10],
                },
            ],
            options: {
                chart: {
                    height: 350,
                    type: "radar",
                },
                stroke: {
                    width: 0,
                },
                fill: {
                    opacity: 0.4,
                },
                markers: {
                    size: 0,
                },
                legend: {
                    offsetY: -10,
                },
                colors: ["#727cf5", "#02a8b5", "#fd7e14"],
                labels: ["2011", "2012", "2013", "2014", "2015", "2016"],
            },
        };
    },
    methods: {
        update() {
            function randomSeries() {
                var arr = [];
                for (var i = 0; i < 6; i++) {
                    arr.push(Math.floor(Math.random() * 100));
                }
                return arr;
            }

            this.series.map(i => {
                i.data = randomSeries()
            })
        },
    },
};
</script>
