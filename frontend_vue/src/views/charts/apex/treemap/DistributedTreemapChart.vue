<template>
<apexchart height="350" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                data: [{
                        x: "New Delhi",
                        y: 218,
                    },
                    {
                        x: "Kolkata",
                        y: 149,
                    },
                    {
                        x: "Mumbai",
                        y: 184,
                    },
                    {
                        x: "Ahmedabad",
                        y: 55,
                    },
                    {
                        x: "Bangaluru",
                        y: 84,
                    },
                    {
                        x: "Pune",
                        y: 31,
                    },
                    {
                        x: "Chennai",
                        y: 70,
                    },
                    {
                        x: "Jaipur",
                        y: 30,
                    },
                    {
                        x: "Surat",
                        y: 44,
                    },
                    {
                        x: "Hyderabad",
                        y: 68,
                    },
                    {
                        x: "Lucknow",
                        y: 28,
                    },
                    {
                        x: "Indore",
                        y: 19,
                    },
                    {
                        x: "Kanpur",
                        y: 29,
                    },
                ],
            }, ],
            options: {
                legend: {
                    show: false,
                },
                chart: {
                    height: 350,
                    type: "treemap",
                },
                title: {
                    text: "Distibuted Treemap (different color for each cell)",
                    align: "center",
                },
                colors: ["#727cf5", "#0acf97", "#fa5c7c", "#6c757d", "#39afd1", "#ffc35a", " #eef2f7", " #313a46"],
                plotOptions: {
                    treemap: {
                        distributed: true,
                        enableShades: false,
                    },
                },
            },
        };
    },
};
</script>
