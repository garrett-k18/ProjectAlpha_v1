<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />
</Layout>
</template>

<script lang="ts">
import Breadcrumb from '@/components/breadcrumb.vue'
import Layout from '@/components/layouts/layout.vue'
export default {
    components: { Breadcrumb, Layout },
    data() {
        return {
            title: 'Starter',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Pages',
                    href: '/',
                },
                {
                    text: 'Starter',
                    active: true,
                },
            ]
        }
    },

}
</script>
