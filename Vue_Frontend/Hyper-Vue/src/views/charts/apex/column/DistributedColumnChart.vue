<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#727cf5", "#6c757d", "#0acf97", "#fa5c7c", "#ffbc00", "#39afd1", "#e3eaef", "#313a46"];
        return {
            series: [{
                data: [21, 22, 10, 28, 16, 21, 13, 30],
            }, ],
            options: {
                chart: {
                    height: 380,
                    type: "bar",
                    toolbar: {
                        show: false,
                    },
                    events: {
                        // click: function (chart, w, e) {
                        //   console.log(chart, w, e);
                        // },
                    },
                },
                colors: colors,
                plotOptions: {
                    bar: {
                        columnWidth: "45%",
                        distributed: true,
                    },
                },
                dataLabels: {
                    enabled: false,
                },

                xaxis: {
                    categories: [
                        "John",
                        "Joe",
                        "Jake",
                        "Amber",
                        "Peter",
                        "Mary",
                        "David",
                        "Lily",
                    ],
                    labels: {
                        style: {
                            colors: colors,
                            fontSize: "14px",
                        },
                    },
                },
                legend: {
                    offsetY: 7,
                },
                grid: {
                    row: {
                        colors: ["transparent", "transparent"], // takes an array which will be repeated on columns
                        opacity: 0.2,
                    },
                    borderColor: "#f1f3fa",
                },
            },
        };
    },
};
</script>
