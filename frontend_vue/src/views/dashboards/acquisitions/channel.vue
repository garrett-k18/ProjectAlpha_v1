<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Channels</h4>
      <a href="javascript:void(0);" class="btn btn-sm btn-light">Export <i class="mdi mdi-download ms-1"></i></a>
    </div>

    <div class="card-body pt-0">
      <b-table-simple responsive centered class="table-sm mb-0 font-14">
        <b-thead head-variant="light">
          <b-tr>
            <b-th>Channel</b-th>
            <b-th>Visits</b-th>
            <b-th style="width: 40%;"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="channel of channelData" :key="channel.name">
            <b-td>{{ channel.name }}</b-td>
            <b-td>{{ channel.visits }}</b-td>
            <b-td>
              <b-progress
                  height="3px"
                  class="mt-2"
                  :value="channel.progressValue"
                  :variant="channel.color"
              ></b-progress>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      channelData: [
        {
          name: 'Direct',
          visits: 2050,
          progressValue: 65,
          color: 'primary',
        },
        {
          name: 'Organic Search',
          visits: 1405,
          progressValue: 45,
          color: 'info',
        },
        {
          name: 'Refferal',
          visits: 750,
          progressValue: 30,
          color: 'warning',
        },
        {
          name: 'Social',
          visits: 540,
          progressValue: 25,
          color: 'danger',
        },
      ],
    }
  },
}
</script>
