<template>
<DefaultLayout body-class="authentication-bg">
    <div class="position-absolute start-0 end-0 start-0 bottom-0 w-100 h-100">
        <svg xmlns='http://www.w3.org/2000/svg' width='100%' height='100%' viewBox='0 0 800 800'>
            <g fill-opacity='0.22'>
                <circle style="fill: rgba(var(--ct-primary-rgb), 0.1);" cx='400' cy='400' r='600' />
                <circle style="fill: rgba(var(--ct-primary-rgb), 0.2);" cx='400' cy='400' r='500' />
                <circle style="fill: rgba(var(--ct-primary-rgb), 0.3);" cx='400' cy='400' r='300' />
                <circle style="fill: rgba(var(--ct-primary-rgb), 0.4);" cx='400' cy='400' r='200' />
                <circle style="fill: rgba(var(--ct-primary-rgb), 0.5);" cx='400' cy='400' r='100' />
            </g>
        </svg>
    </div>

    <div class="account-pages pt-2 pt-sm-5 pb-4 pb-sm-5 position-relative">
        <b-container>
            <b-row class="justify-content-center">
                <b-col xxl="4" lg="5">
                    <div class="card">
                        <!-- Logo -->
                        <div class="card-header py-4 text-center bg-primary">
                            <router-link to="/">
                                <span><img src="../../assets/images/logo.png" alt="logo" height="22"></span>
                            </router-link>
                        </div>

                        <div class="card-body p-4">

                            <div class="text-center">
                                <img src="../../assets/images/svg/startman.svg" height="120" alt="File not found Image">

                                <h1 class="text-error mt-4">500</h1>
                                <h4 class="text-uppercase text-danger mt-3">Internal Server Error</h4>
                                <p class="text-muted mt-3">Why not try refreshing your page? or you can contact <a href="" class="text-muted"><b>Support</b></a></p>

                                <router-link class="btn btn-info mt-3" to="/"><i class="mdi mdi-reply"></i> Return Home</router-link>
                            </div>

                        </div> <!-- end card-body-->
                    </div>
                    <!-- end card-->

                </b-col> <!-- end col -->
            </b-row>
            <!-- end row -->
        </b-container>
        <!-- end container -->
    </div>
    <!-- end page -->

    <Footer2 />
</DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from '@/components/layouts/default-layout.vue';
import Footer2 from '@/components/layouts/partials/footer-2.vue';
export default {
    components: { DefaultLayout, Footer2 },
}
</script>
