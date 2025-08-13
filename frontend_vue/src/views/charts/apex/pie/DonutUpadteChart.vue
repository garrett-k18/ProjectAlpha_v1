<template>
<div dir="ltr">
    <apexchart height="320" :options="options" :series="series"></apexchart>
</div>
<div class="text-center mt-2">
    <b-button variant="primary" size="sm" id="randomize" @click="randomize">
        RANDOMIZE
    </b-button>
    <b-button variant="primary" size="sm" id="add" @click="appendData">ADD</b-button>
    <b-button variant="primary" size="sm" id="remove" @click="removeData">REMOVE</b-button>
    <b-button variant="primary" size="sm" id="reset" @click="reset">RESET</b-button>
</div>
</template>

<script lang="ts">
export default {
    data() {
        let series = [44, 55, 13, 33]
        return {
            series,
            options: {
                chart: {
                    height: 320,
                    type: 'donut',
                },
                dataLabels: {
                    enabled: false
                },
                colors: ["#727cf5", "#6c757d", "#0acf97", "#fa5c7c"],
                legend: {
                    show: true,
                    position: 'bottom',
                    horizontalAlign: 'center',
                    verticalAlign: 'middle',
                    floating: false,
                    fontSize: '14px',
                    offsetX: 0,
                    offsetY: 7
                },
                responsive: [{
                    breakpoint: 600,
                    options: {
                        chart: {
                            height: 240
                        },
                        legend: {
                            show: false
                        },
                    }
                }]
            },
        };
    },

    methods: {
        appendData() {
            let arr = this.series.map(function () {
                return Math.floor(Math.random() * (100 - 1 + 1)) + 1;
            });
            arr.push(Math.floor(Math.random() * (100 - 1 + 1)) + 1);
            return this.series = arr;
        },

        removeData() {
            let arr = this.series.map(function () {
                return Math.floor(Math.random() * (100 - 1 + 1)) + 1;
            });
            arr.pop();
            return this.series = arr;
        },

        randomize() {
            return this.series = this.series.map(() => Math.floor(Math.random() * (100 - 1 + 1)) + 1);
        },

        reset() {
            return this.series = [44, 55, 13, 33];
        }
    }
};
</script>
