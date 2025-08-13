<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data: function () {
        return {
            series: [{
                    name: 'Product 1',
                    data: this.generateData1(new Date('11 Feb 2017 GMT').getTime(), 20, {
                        min: 10,
                        max: 60
                    })
                },
                {
                    name: 'Product 2',
                    data: this.generateData1(new Date('11 Feb 2017 GMT').getTime(), 20, {
                        min: 10,
                        max: 60
                    })
                },
                {
                    name: 'Product 3',
                    data: this.generateData1(new Date('11 Feb 2017 GMT').getTime(), 20, {
                        min: 10,
                        max: 60
                    })
                },
                {
                    name: 'Product 4',
                    data: this.generateData1(new Date('11 Feb 2017 GMT').getTime(), 20, {
                        min: 10,
                        max: 60
                    })
                }
            ],
            options: {
                chart: {
                    height: 380,
                    type: 'bubble',
                    toolbar: {
                        show: false
                    }
                },
                dataLabels: {
                    enabled: false
                },
                fill: {
                    type: 'gradient',
                },
                colors: ["#727cf5", "#0acf97", "#fa5c7c", "#39afd1"],
                xaxis: {
                    tickAmount: 12,
                    type: 'datetime',

                    labels: {
                        rotate: 0,
                    }
                },
                yaxis: {
                    max: 70
                },
                legend: {
                    offsetY: 7,
                },
                grid: {
                    borderColor: '#f1f3fa',
                    padding: {
                        bottom: 5
                    }
                }
            }
        }
    },
    methods: {
        generateData1(baseval1: number, count: number, yrange: any) {
            var i = 0;
            var series = [];
            while (i < count) {
                //var x =Math.floor(Math.random() * (750 - 1 + 1)) + 1;;
                var y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;
                var z = Math.floor(Math.random() * (75 - 15 + 1)) + 15;

                series.push([baseval1, y, z]);
                baseval1 += 86400000;
                i++;
            }
            return series;
        }
    },
}
</script>
