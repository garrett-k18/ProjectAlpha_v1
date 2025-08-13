<template>
  <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">{{ title }}</h4>
      <div class="dropdown float-end">
        <b-dropdown toggle-class="arrow-none card-drop p-0" variant="white" right>
          <template v-slot:button-content>
            <i class="mdi mdi-dots-vertical"></i>
          </template>
          <b-dropdown-item href="javascript:void(0);">Settings</b-dropdown-item>
          <b-dropdown-item href="javascript:void(0);">Action</b-dropdown-item>
        </b-dropdown>
      </div>
      </div>


      <simplebar class="card-body py-0 mb-3" :style="`max-height:${transactionWindowHeight}`">
        <b-row v-for="data of transactions" :key="data.title" class="py-1 align-items-center">
          <b-col class="col-auto">
            <i :class="`mdi ${data.icon} text-${data.color} font-18`"></i>
          </b-col>
          <b-col class="pl-0">
            <a href="javascript:void(0);" class="text-body">{{data.title}}</a>
            <p class="mb-0 text-muted">
              <small>{{data.date}}</small>
            </p>
          </b-col>
          <b-col class="col-auto">
            <span :class="`text-${data.color} font-weight-bold pr-2`">{{data.amount }}</span>
          </b-col>
        </b-row>
      </simplebar>
    <!-- end card-body -->
    </div>
  <!-- end card -->
</template>

<script lang="ts">
import simplebar from 'simplebar-vue'

/**
 * Transactions component
 * 1. User specifies the title of window using the 'title' input property.
 * 2. Window height set using the 'transactionWindowHeight' input property. Height would count in pixel.
 * 3. Transactions array specify - title, icon, date, amount and color.
 *     title - the transaction name specify in title
 *     icon - icon name specify using
 *     date - Transaction which day done specify using date.
 *     amount - transaction amount specify using the
 *     color - Icon and amount color specify using color. Success defines the profit and danger define the loss.
 */
export default {
  components: {
    simplebar,
  },
  props: {
    title: {
      type: String,
      default: 'Transactions',
    },
    transactionWindowHeight: {
      type: String,
      default: '320px',
    },
    transactions: {
      type: Array,
      default: function() {
        return []
      },
    },
  },
}
</script>