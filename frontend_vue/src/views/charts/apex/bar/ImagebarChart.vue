<template>
<apexchart height="450" :options="options" :series="series"></apexchart>
</template>

<script>
import image1 from '@/assets/images/small/small-4.jpg'
export default {
    data: function () {
        var labels = Array.apply(null, { length: 39 }).map(function (el, index) {
            return index + 1;
        });
        return {
            series: [{
                name: 'coins',
                data: [2, 4, 3, 4, 3, 5, 5, 6.5, 6, 5, 4, 5, 8, 7, 7, 8, 8, 10, 9, 9, 12, 12, 11, 12, 13, 14, 16, 14, 15, 17, 19, 21]
            }],
            options: {
                chart: {
                    height: 450,
                    type: 'bar',
                    toolbar: {
                        show: false
                    },
                    animations: {
                        enabled: false
                    }
                },
                plotOptions: {
                    bar: {
                        horizontal: true,
                        barHeight: '100%',

                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    colors: ["#fff"],
                    width: 0.2
                },
                labels: labels,
                yaxis: {
                    axisBorder: {
                        show: false
                    },
                    axisTicks: {
                        show: false
                    },
                    labels: {
                        show: false
                    },
                    title: {
                        text: 'Weight',
                    },
                },
                xaxis: {
                    axisBorder: {
                        show: false,
                    }
                },
                grid: {
                    position: 'back',
                    borderColor: '#f1f3fa'
                },
                fill: {
                    type: "image",
                    opacity: 0.87,
                    image: {
                        src: image1,
                        width: 466,
                        height: 406
                    }
                },
            }
        }
    }
}
</script>
