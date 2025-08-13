<template>
<apexchart height="630" :options="options" :series="series"></apexchart>
</template>

<script lang="ts">
export default {
    data() {
        return {
            series: [76],
            options: {
                chart: {
                    type: 'radialBar',
                    offsetY: -20,
                    sparkline: {
                        enabled: true
                    }
                },
                plotOptions: {
                    radialBar: {
                        startAngle: -90,
                        endAngle: 90,
                        track: {
                            background: "rgba(170,184,197, 0.2)",
                            strokeWidth: '97%',
                            margin: 5, // margin is in pixels
                            dropShadow: {
                                top: 2,
                                left: 0,
                                color: '#eef2f7',
                                opacity: 1,
                                blur: 2
                            }
                        },
                        dataLabels: {
                            name: {
                                show: false
                            },
                            value: {
                                offsetY: -2,
                                fontSize: '22px'
                            }
                        }
                    }
                },
                grid: {
                    padding: {
                        top: -10
                    }
                },
                colors: ["#8f75da", "#3e60d5" ],
                labels: ['Average Results'],
            }
        };
    },
};
</script>
