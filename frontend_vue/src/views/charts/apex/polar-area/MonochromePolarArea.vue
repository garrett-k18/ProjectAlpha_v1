<template>
<apexchart height="380" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [42, 47, 52, 58, 65],
            options: {
                chart: {
                    height: 380,
                    type: 'polarArea'
                },
                labels: ['Rose A', 'Rose B', 'Rose C', 'Rose D', 'Rose E'],
                fill: {
                    opacity: 1
                },
                stroke: {
                    width: 1
                },
                yaxis: {
                    show: false
                },
                legend: {
                    position: 'bottom'
                },
                plotOptions: {
                    polarArea: {
                        rings: {
                            strokeWidth: 0
                        },
                        spokes: {
                            strokeWidth: 0
                        },
                    }
                },
                theme: {
                    monochrome: {
                        enabled: true,
                        shadeTo: 'light',
                        color: '#727cf5',
                        shadeIntensity: 0.6
                    }
                }
            },
        };
    },
};
</script>
