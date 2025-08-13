<template>
<Layout>
    <Breadcrumb :items="items" :title="title" />

    <b-row class="justify-content-center">
        <b-col lg="4">
            <div class="text-center">
                <img src="../../assets/images/svg/file-searching.svg" height="90" alt="File not found Image">

                <h1 class="text-error mt-4">404</h1>
                <h4 class="text-uppercase text-danger mt-3">Page Not Found</h4>
                <p class="text-muted mt-3">It's looking like you may have taken a wrong turn. Don't worry... it
                    happens to the best of us. Here's a
                    little tip that might help you get back on track.</p>

                <router-link class="btn btn-info mt-3" to="/"><i class="mdi mdi-reply"></i> Return Home</router-link>
            </div> <!-- end /.text-center-->
        </b-col> <!-- end col-->
    </b-row>
</Layout>
</template>

<script lang="ts">
import Layout from '@/components/layouts/layout.vue'
import Breadcrumb from '@/components/breadcrumb.vue'
export default {
    components: { Layout, Breadcrumb },
    data() {
        return {
            title: '404 Error',
            items: [{
                    text: 'Hyper',
                    href: '/',
                },
                {
                    text: 'Pages',
                    href: '/',
                },
                {
                    text: '404 Error',
                    active: true,
                },
            ]
        }
    },
}
</script>
