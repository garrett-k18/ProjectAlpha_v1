<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                name: "Servings",
                data: [44, 55, 41, 67, 22, 43, 21, 33, 45, 31, 87, 65, 35],
            }, ],
            options: {
                annotations: {
                    points: [{
                        x: "Bananas",
                        seriesIndex: 0,
                        label: {
                            borderColor: "#3e60d5",
                            offsetY: 0,
                            style: {
                                color: "#fff",
                                background: "#3e60d5",
                            },
                            text: "Bananas are good",
                        },
                    }, ],
                },
                chart: {
                    height: 380,
                    type: "bar",
                    toolbar: {
                        show: false,
                    },
                },
                plotOptions: {
                    bar: {
                        columnWidth: "50%",
                        endingShape: "rounded",
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: 2,
                },
                colors: ["#fa5c7c"],

                grid: {
                    borderColor: "#f1f3fa",
                    padding: {
                        top: 0,
                        right: -2,
                        bottom: -35,
                        left: 10,
                    },
                },
                xaxis: {
                    labels: {
                        rotate: -45,
                    },
                    categories: [
                        "Apples",
                        "Oranges",
                        "Strawberries",
                        "Pineapples",
                        "Mangoes",
                        "Bananas",
                        "Blackberries",
                        "Pears",
                        "Watermelons",
                        "Cherries",
                        "Pomegranates",
                        "Tangerines",
                        "Papayas",
                    ],
                },
                yaxis: {
                    title: {
                        text: "Servings",
                    },
                },
                fill: {
                    type: "gradient",
                    gradient: {
                        shade: "light",
                        type: "horizontal",
                        shadeIntensity: 0.25,
                        gradientToColors: undefined,
                        inverseColors: true,
                        opacityFrom: 0.85,
                        opacityTo: 0.85,
                        stops: [50, 0, 100],
                    },
                },
            },
        };
    },
};
</script>
