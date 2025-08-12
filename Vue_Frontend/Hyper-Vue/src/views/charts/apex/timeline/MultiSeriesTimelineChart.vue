<template>
<apexchart hieght="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
import moment from "moment";
export default {
    data() {
        return {
            series: [{
                    name: "Bob",
                    data: [{
                            x: "Design",
                            y: [
                                new Date("2019-03-05").getTime(),
                                new Date("2019-03-08").getTime(),
                            ],
                        },
                        {
                            x: "Code",
                            y: [
                                new Date("2019-03-08").getTime(),
                                new Date("2019-03-11").getTime(),
                            ],
                        },
                        {
                            x: "Test",
                            y: [
                                new Date("2019-03-11").getTime(),
                                new Date("2019-03-16").getTime(),
                            ],
                        },
                    ],
                },
                {
                    name: "Joe",
                    data: [{
                            x: "Design",
                            y: [
                                new Date("2019-03-02").getTime(),
                                new Date("2019-03-05").getTime(),
                            ],
                        },
                        {
                            x: "Code",
                            y: [
                                new Date("2019-03-06").getTime(),
                                new Date("2019-03-09").getTime(),
                            ],
                        },
                        {
                            x: "Test",
                            y: [
                                new Date("2019-03-10").getTime(),
                                new Date("2019-03-19").getTime(),
                            ],
                        },
                    ],
                },
            ],
            options: {
                chart: {
                    height: 350,
                    type: "rangeBar",
                    toolbar: {
                        show: false,
                    },
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                    },
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val: any[]) {
                        var a = moment(val[0])
                        var b = moment(val[1])
                        var diff = b.diff(a, 'days')
                        return diff + (diff > 1 ? ' days' : ' day')
                    },
                },
                fill: {
                    type: "gradient",
                    gradient: {
                        shade: "light",
                        type: "vertical",
                        shadeIntensity: 0.25,
                        gradientToColors: undefined,
                        inverseColors: true,
                        opacityFrom: 1,
                        opacityTo: 1,
                        stops: [50, 0, 100, 100],
                    },
                },
                colors: ["#6c757d","#39afd1"],
                xaxis: {
                    type: "datetime",
                },
                legend: {
                    position: "top",
                },
            },
        };
    },
};
</script>
