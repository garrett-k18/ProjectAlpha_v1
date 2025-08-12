<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">Money History</h4>

      <b-dropdown class="float-end" toggle-class="arrow-none card-drop p-0" variant="black" right>
        <template v-slot:button-content>
          <i class="mdi mdi-dots-vertical"></i>
        </template>
        <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-cached me-1"></i>Refresh</b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);"><i class="mdi mdi-circle-edit-outline me-1"></i>Edit
        </b-dropdown-item>
        <b-dropdown-item href="javascript:void(0);" class="text-danger"><i class="mdi mdi-delete-outline me-1"></i>Remove
        </b-dropdown-item>
      </b-dropdown>
    </div>

    <div class="card-body py-0">
      <div v-for="(item,index) in historyData" :key="index" class="border border-light p-3 rounded mb-3">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <p class="font-18 mb-1">{{ item.title }}</p>
            <h3 :class="`text-${item.color} my-0`">${{ item.number }}</h3>
          </div>
          <div class="avatar-sm">
            <span :class="`avatar-title bg-${item.color} rounded-circle h3 my-0`">
              <i :class="`mdi ${item.icon}`"></i>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      historyData: [
        {
          title: 'Income',
          number: '2,76,548',
          icon: 'mdi-arrow-up-bold-outline',
          color: 'primary'
        },
        {
          title: 'Expenses',
          number: '50,216',
          icon: 'mdi-arrow-down-bold-outline',
          color: 'danger'
        },
        {
          title: 'Transfer',
          number: '98,100',
          icon: 'mdi-swap-horizontal',
          color: 'success'
        },
      ]
    }
  }
}
</script>
