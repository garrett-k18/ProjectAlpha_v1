<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script>
export default {
    data: function () {
        const colors = ["#727cf5"];
        return {
            series: [{
                name: 'Inflation',
                data: [2.3, 3.1, 4.0, 10.1, 4.0, 3.6, 3.2, 2.3, 1.4, 0.8, 0.5, 0.2]
            }],
            options: {
                chart: {
                    height: 380,
                    type: 'bar',
                    toolbar: {
                        show: false
                    }
                },
                plotOptions: {
                    bar: {
                        borderRadius: 10,
                        dataLabels: {
                            position: 'top', // top, center, bottom
                        },
                    }
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val) {
                        return val + "%";
                    },
                    offsetY: -25,
                    style: {
                        fontSize: '12px',
                        colors: ["#304758"]
                    }
                },
                colors: colors,
                legend: {
                    show: true,
                    horizontalAlign: "center",
                    offsetX: 0,
                    offsetY: -5,
                },
                xaxis: {
                    categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                    position: 'top',
                    labels: {
                        offsetY: 0,
                    },
                    axisBorder: {
                        show: false
                    },
                    axisTicks: {
                        show: false
                    },
                    crosshairs: {
                        fill: {
                            type: 'gradient',
                            gradient: {
                                colorFrom: '#D8E3F0',
                                colorTo: '#BED1E6',
                                stops: [0, 100],
                                opacityFrom: 0.4,
                                opacityTo: 0.5,
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        offsetY: -10,
                    }
                },
                fill: {
                    gradient: {
                        enabled: false,
                        shade: 'light',
                        type: "horizontal",
                        shadeIntensity: 0.25,
                        gradientToColors: undefined,
                        inverseColors: true,
                        opacityFrom: 1,
                        opacityTo: 1,
                        stops: [50, 0, 100, 100]
                    },
                },
                yaxis: {
                    axisBorder: {
                        show: false
                    },
                    axisTicks: {
                        show: false,
                    },
                    labels: {
                        show: false,
                        formatter: function (val) {
                            return val + "%";
                        }
                    }

                },
                title: {
                    text: 'Monthly Inflation in Argentina, 2002',
                    floating: true,
                    offsetY: 360,
                    align: 'center',
                    style: {
                        color: '#444'
                    }
                },
                grid: {
                    row: {
                        colors: ['transparent', 'transparent'], // takes an array which will be repeated on columns
                        opacity: 0.2
                    },
                    borderColor: '#f1f3fa'
                }
            }
        }
    }
}
</script>
