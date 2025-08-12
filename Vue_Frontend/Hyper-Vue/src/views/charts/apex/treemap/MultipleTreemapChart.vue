<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                    name: "Desktops",
                    data: [{
                            x: "ABC",
                            y: 10,
                        },
                        {
                            x: "DEF",
                            y: 60,
                        },
                        {
                            x: "XYZ",
                            y: 41,
                        },
                    ],
                },
                {
                    name: "Mobile",
                    data: [{
                            x: "ABCD",
                            y: 10,
                        },
                        {
                            x: "DEFG",
                            y: 20,
                        },
                        {
                            x: "WXYZ",
                            y: 51,
                        },
                        {
                            x: "PQR",
                            y: 30,
                        },
                        {
                            x: "MNO",
                            y: 20,
                        },
                        {
                            x: "CDE",
                            y: 30,
                        },
                    ],
                },
            ],
            options: {
                legend: {
                    show: false,
                },
                chart: {
                    height: 350,
                    type: "treemap",
                },
                colors: ["#fa5c7c", "#6c757d"],
                title: {
                    text: "Multi-dimensional Treemap",
                    align: "center",
                },
            },
        };
    },
};
</script>
