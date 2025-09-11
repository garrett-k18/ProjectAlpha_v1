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
                                <span><img src="https://placehold.co/180x40/4f46e5/ffffff/png?text=ProjectAlpha" alt="ProjectAlpha" height="40"></span>
                            </router-link>
                        </div>

                        <div class="card-body p-4">

                            <div class="text-center w-75 m-auto">
                                <h4 class="text-dark-50 text-center mt-0 fw-bold">Reset Password</h4>
                                <p class="text-muted mb-4">Enter your email address and we'll send you an email with instructions to reset your password.</p>
                            </div>

                            <b-form action="#">
                                <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                                    <b-form-input type="email" id="emailaddress" required placeholder="Enter your email" />
                                </b-form-group>

                                <div class="mb-0 text-center">
                                    <b-button variant="primary" type="submit">Reset Password</b-button>
                                </div>
                            </b-form>
                        </div> <!-- end card-body-->
                    </div>
                    <!-- end card -->

                    <b-row class="mt-3">
                        <b-col cols="12" class="text-center">
                            <p class="text-muted">Back to <router-link to="/login" class="text-muted ms-1"><b>Log In</b></router-link>
                            </p>
                        </b-col> <!-- end col -->
                    </b-row>
                    <!-- end row -->

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
