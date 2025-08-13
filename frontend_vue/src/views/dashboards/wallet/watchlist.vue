<template>
  <div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h4 class="header-title">My Watchlist</h4>

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


    <div class="card-body pt-0 mb-2" data-simplebar style="max-height: 319px;">
      <div v-for="(item,index) in watchlistData" :key="index">
        <div class="d-flex align-items-center">
          <div class="flex-shrink-0">
            <div class="avatar-sm rounded">
              <span class="avatar-title rounded-circle h3 my-0"
                    :class="`text-${item.color} bg-${item.color}-lighten border border-${item.color}`">
                <i :class="`mdi ${item.icon}`"></i>
              </span>
            </div>
          </div>
          <div class="flex-grow-1 ms-2">
            <h4 class="mt-0 mb-1 font-16 fw-semibold">{{ item.title }}</h4>
            <p class="mb-0 text-muted">{{ item.amount }}</p>
          </div>
          <p class="mb-0" :class="item.growthIcon == 'mdi-trending-up' ? 'text-success' : 'text-danger'"><i
              :class="`mdi ${item.growthIcon} me-1`"></i>{{ item.growth }}</p>
        </div>

        <hr v-if="index != 5">
      </div>

    </div>
  </div>
</template>

<script lang="ts">
export default {
  data() {
    return {
      watchlistData: [
        {
          icon: 'mdi-currency-btc',
          title: 'Bitcoin (BTC)',
          amount: '48,665.80',
          growth: '10%',
          growthIcon: 'mdi-trending-up',
          color: 'warning'
        },
        {
          icon: 'mdi-currency-ngn',
          title: 'Nigerian naira (NGN)',
          amount: '$0.0024',
          growth: '12%',
          growthIcon: 'mdi-trending-down',
          color: 'success'
        },
        {
          icon: 'mdi-currency-gbp',
          title: 'Pound sterling (GBP)',
          amount: '$1.33',
          growth: '15%',
          growthIcon: 'mdi-trending-up',
          color: 'danger'
        },
        {
          icon: 'mdi-currency-ils',
          title: 'Israeli shekels (ILS)',
          amount: '$0.32',
          growth: '11%',
          growthIcon: 'mdi-trending-up',
          color: 'primary'
        },
        {
          icon: 'mdi-currency-kzt',
          title: 'Kazakhstani tenge (KZT)',
          amount: '$0.0023',
          growth: '10%',
          growthIcon: 'mdi-trending-down',
          color: 'info'
        },
        {
          icon: 'mdi-currency-rub',
          title: 'Russian ruble (RUB)',
          amount: '$0.014',
          growth: '18%',
          growthIcon: 'mdi-trending-up',
          color: 'secondary'
        },
      ]
    }
  }
}
</script>
