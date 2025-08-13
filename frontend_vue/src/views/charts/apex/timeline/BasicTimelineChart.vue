<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [{
                data: [{
                        x: "Code",
                        y: [
                            new Date("2019-03-02").getTime(),
                            new Date("2019-03-04").getTime(),
                        ],
                    },
                    {
                        x: "Test",
                        y: [
                            new Date("2019-03-04").getTime(),
                            new Date("2019-03-08").getTime(),
                        ],
                    },
                    {
                        x: "Validation",
                        y: [
                            new Date("2019-03-08").getTime(),
                            new Date("2019-03-12").getTime(),
                        ],
                    },
                    {
                        x: "Deployment",
                        y: [
                            new Date("2019-03-12").getTime(),
                            new Date("2019-03-18").getTime(),
                        ],
                    },
                ],
            }, ],
            options: {
                chart: {
                    height: 350,
                    type: "rangeBar",
                    toolbar: {
                        show: false,
                    },
                },
                colors: ["#fa6767"],
                plotOptions: {
                    bar: {
                        horizontal: true,
                    },
                },
                xaxis: {
                    type: "datetime",
                },
            },
        };
    },
};
</script>
