<template>
  <div class="card widget-inline">
    <div class="card-body p-0">
      <b-row class="g-0">

        <b-col sm="6" lg="3" v-for="(data,index) of statData" :key="data.text">
          <div class="card rounded-0 shadow-none m-0 border-start border-light">
            <div class="card-body text-center">
              <i :class="`${data.icon} text-muted font-24`"></i>
              <h3>
                <span>{{ data.value }}</span>
                <i v-if="index == 3" class="mdi mdi-arrow-up text-success"></i>
              </h3>
              <p class="text-muted font-15 mb-0">{{ data.text }}</p>
            </div>
          </div>
        </b-col>

      </b-row>
    </div>
  </div>
</template>


<script lang="ts">
export default {
  data() {
    return {
      statData: [
        {
          icon: 'ri-briefcase-line',
          value: '29',
          text: 'Total Projects',
        },
        {
          icon: 'ri-list-check-2',
          value: '715',
          text: 'Total Tasks',
        },
        {
          icon: 'ri-group-line',
          value: '31',
          text: 'Members',
        },
        {
          icon: 'ri-line-chart-line',
          value: '93%',
          text: 'Productivity',
        },
      ],
    }
  },
}
</script>


