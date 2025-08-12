<template>
  <Layout>
    <Breadcrumb :title="title" :items="items"/>
    <b-row>
      <b-col xxl="9">
        <Stats/>

        <b-row>
          <b-col cols="12">
            <BalanceStatus/>
          </b-col>
        </b-row>
      </b-col>

      <b-col xxl="3">
        <b-row>
          <b-col xxl="12" md="6">
            <Card/>
          </b-col>

          <b-col xxl="12" md="6">
            <Watchlist/>
          </b-col>
        </b-row>

      </b-col>
    </b-row>

    <b-row>
      <b-col xxl="3" md="6">
        <MoneyHistory/>
      </b-col>

      <b-col xxl="3" md="6">
        <Merchants/>
      </b-col>

      <b-col xxl="6">
        <Transactions/>
      </b-col>
    </b-row>
  </Layout>
</template>

<script lang="ts">
import Layout from "@/components/layouts/layout.vue";
import Breadcrumb from "@/components/breadcrumb.vue";
import MoneyHistory from "@/views/dashboards/wallet/money-history.vue";
import Merchants from "@/views/dashboards/wallet/merchants.vue";
import Transactions from "@/views/dashboards/wallet/transactions.vue";
import Watchlist from "@/views/dashboards/wallet/watchlist.vue";
import BalanceStatus from "@/views/dashboards/wallet/balance-status.vue";
import Card from "@/views/dashboards/wallet/card.vue";
import Stats from "@/views/dashboards/wallet/stats.vue";

export default {
  components: {Stats, Card, BalanceStatus, Watchlist, Transactions, Merchants, MoneyHistory, Breadcrumb, Layout},
  data(){
    return{
      title: 'E-Wallet',
      items: [
        {
          text: 'Hyper',
          href: '/',
        },
        {
          text: 'Dashboard',
          href: '/',
        },
        {
          text: 'E-Wallet',
          active: true,
        },
      ],
    }
  }

}
</script>
