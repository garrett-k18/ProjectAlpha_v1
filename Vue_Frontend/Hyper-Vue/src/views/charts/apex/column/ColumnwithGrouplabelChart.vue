<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        const colors = ["#39afd1","#0acf97","#e3eaef"];
        return {
            series: [{
                name: "Sales",
                data: [{
                        x: "2020/01/01",
                        y: 400,
                    },
                    {
                        x: "2020/04/01",
                        y: 430,
                    },
                    {
                        x: "2020/07/01",
                        y: 448,
                    },
                    {
                        x: "2020/10/01",
                        y: 470,
                    },
                    {
                        x: "2021/01/01",
                        y: 540,
                    },
                    {
                        x: "2021/04/01",
                        y: 580,
                    },
                    {
                        x: "2021/07/01",
                        y: 690,
                    },
                    {
                        x: "2021/10/01",
                        y: 690,
                    },
                ],
            }, ],
            options: {
                chart: {
                    type: "bar",
                    height: 380,
                    toolbar: {
                        show: false,
                    },
                },
                plotOptions: {
                    bar: {
                        horizontal: false,
                        columnWidth: "45%",
                    },
                },
                colors: colors,
                xaxis: {
                    type: "category",
                    labels: {
                        formatter: function (val: number) {
                            // return "Q" + dayjs(val).quarter()
                        },
                    },
                    group: {
                        style: {
                            fontSize: "10px",
                            fontWeight: 700,
                        },
                        groups: [{
                                title: "2020",
                                cols: 4,
                            },
                            {
                                title: "2021",
                                cols: 4,
                            },
                        ],
                    },
                },
                tooltip: {
                    x: {
                        formatter: function (val: number) {
                            // return "Q" + dayjs(val).quarter() + " " + dayjs(val).format("YYYY")
                        },
                    },
                },
            },
        };
    },
};
</script>
