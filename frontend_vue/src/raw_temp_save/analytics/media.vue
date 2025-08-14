<template>
  <div class="card">
    <div class="d-flex card-header justify-content-between align-items-center">
      <h4 class="header-title">Social Media Traffic</h4>
      <a href="javascript:void(0);" class="btn btn-sm btn-light">Export <i class="mdi mdi-download ms-1"></i></a>
    </div>

    <div class="card-body pt-0">
      <b-table-simple responsive centered class="table-sm mb-0 font-14">
        <b-thead thread-variant="light">
          <b-tr>
            <b-th>Network</b-th>
            <b-th>Visits</b-th>
            <b-th style="width: 40%;"></b-th>
          </b-tr>
        </b-thead>
        <b-tbody>
          <b-tr v-for="media of mediaData" :key="media.network">
            <b-td>{{ media.network }}</b-td>
            <b-td>{{ media.visits }}</b-td>
            <b-td>
              <b-progress height="3px" class="mt-2" :value="media.progressValue"></b-progress>
            </b-td>
          </b-tr>
        </b-tbody>
      </b-table-simple>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      mediaData: [
        {
          network: 'Facebook',
          visits: 2250,
          progressValue: 65,
        },
        {
          network: 'Instagram',
          visits: 1501,
          progressValue: 45,
        },
        {
          network: 'Twitter',
          visits: 750,
          progressValue: 30,
        },
        {
          network: 'LinkedIn',
          visits: 540,
          progressValue: 25,
        },
      ],
    }
  },
}
</script>