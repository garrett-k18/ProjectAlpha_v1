<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Engagement Overview</h4>
      <a href="javascript:void(0);" class="btn btn-sm btn-light">Export <i class="mdi mdi-download ms-1"></i></a>
    </div>

    <div class="card-body pt-0">
      <b-table-simple responsive centered class="table-sm mb-0 font-14">
        <b-thead thread-variant="light">
          <b-tr>
            <b-th>Duration (Secs)</b-th>
            <b-th style="width: 30%;">Sessions</b-th>
            <b-th style="width: 30%;">Views</b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="data of engagementData" :key="data.duration">
            <b-td>{{ data.duration }}</b-td>
            <b-td>{{ data.sessions }}</b-td>
            <b-td>{{ data.views }}</b-td>
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
      engagementData: [
        {
          duration: '0-30',
          sessions: 2250,
          views: 4250,
        },
        {
          duration: '31-60',
          sessions: 1501,
          views: 2050,
        },
        {
          duration: '61-120',
          sessions: 750,
          views: 1600,
        },
        {
          duration: '121-240',
          sessions: 540,
          views: 1040,
        },
      ],
    }
  },
}
</script>