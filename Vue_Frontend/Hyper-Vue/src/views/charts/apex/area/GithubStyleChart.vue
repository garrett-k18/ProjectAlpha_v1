<template>
<apexchart type="area" height="160" :options="optionsarea1" :series="seriesarea1"></apexchart>
<div class="pt-2 pb-2">
    <b-row class="align-items-center">
        <b-col class="col-auto">
            <img src="@/assets/images/users/avatar-2.jpg" class="avatar-xs rounded" alt="file-image" />
        </b-col>
        <b-col class="ps-0">
            <a href="javascript:void(0);" class="text-muted fw-bold">Coderthemes</a>
        </b-col>
    </b-row>
</div>
<apexchart type="area" height="200" :options="optionsarea2" :series="seriesarea2"></apexchart>
</template>

<script lang="ts">
import { githubdata } from "../data";
export default {
    data() {
        return {
            seriesarea1: [{
                name: "commits",
                data: githubdata.series,
            }, ],
            optionsarea1: {
                chart: {
                    height: 175,
                    type: "area",
                    toolbar: {
                        autoSelected: "selection",
                    },
                    brush: {
                        enabled: true,
                        target: "chartyear",
                    },
                    selection: {
                        enabled: true,
                        xaxis: {
                            min: new Date("05 Jan 2014").getTime(),
                            max: new Date("04 Jan 2015").getTime(),
                        },
                    },
                },
                colors: ["#7BD39A"],
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: 0,
                    curve: "smooth",
                },

                fill: {
                    opacity: 1,
                    type: "solid",
                },
                legend: {
                    position: "top",
                    horizontalAlign: "left",
                },
                xaxis: {
                    type: "datetime",
                },
            },

            seriesarea2: [{
                name: "commits",
                data: githubdata.series,
            }, ],
            optionsarea2: {
                chart: {
                    id: "chartyear",
                    type: "area",
                    height: 200,
                    toolbar: {
                        show: false,
                        autoSelected: "pan",
                    },
                },
                colors: ["#FF7F00"],
                stroke: {
                    width: 0,
                    curve: "smooth",
                },
                dataLabels: {
                    enabled: false,
                },
                fill: {
                    opacity: 1,
                    type: "solid",
                },

                yaxis: {
                    tickAmount: 10,
                    labels: {
                        show: false,
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
