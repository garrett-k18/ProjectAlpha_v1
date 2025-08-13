<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
import moment from 'moment';

export default {
    data() {
        const colors = ["#727cf5", "#0acf97", "#fa5c7c", "#6c757d", "#39afd1"];
        return {
            series: [{
                data: [{
                        x: 'Analysis',
                        y: [
                            new Date('2019-02-27').getTime(),
                            new Date('2019-03-04').getTime()
                        ],
                        fillColor: colors[0]
                    },
                    {
                        x: 'Design',
                        y: [
                            new Date('2019-03-04').getTime(),
                            new Date('2019-03-08').getTime()
                        ],
                        fillColor: colors[1]
                    },
                    {
                        x: 'Coding',
                        y: [
                            new Date('2019-03-07').getTime(),
                            new Date('2019-03-10').getTime()
                        ],
                        fillColor: colors[2]
                    },
                    {
                        x: 'Testing',
                        y: [
                            new Date('2019-03-08').getTime(),
                            new Date('2019-03-12').getTime()
                        ],
                        fillColor: colors[3]
                    },
                    {
                        x: 'Deployment',
                        y: [
                            new Date('2019-03-12').getTime(),
                            new Date('2019-03-17').getTime()
                        ],
                        fillColor: colors[4]
                    }
                ]
            }],
            options: {
                chart: {
                    height: 350,
                    type: 'rangeBar',
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        distributed: true,
                        dataLabels: {
                            hideOverflowingLabels: false
                        }
                    }
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val: any[], opts: any) {
                        var label = opts.w.globals.labels[opts.dataPointIndex]
                        var a = moment(val[0])
                        var b = moment(val[1])
                        var diff = b.diff(a, 'days')
                        return label + ': ' + diff + (diff > 1 ? ' days' : ' day')
                    },
                    style: {
                        colors: ['#f3f4f5', '#fff']
                    }
                },
                xaxis: {
                    type: 'datetime'
                },
                yaxis: {
                    show: false
                },
                grid: {
                    row: {
                        colors: ['#f3f4f5', '#fff'],
                        opacity: 1
                    },
                    padding: {
                        top: -15,
                        right: 10,
                        bottom: -15,
                        left: -10,
                    }
                }
            },
        };
    },
};
</script>
