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
                        <!-- Logo-->
                        <div class="card-header py-4 text-center bg-primary">
                            <router-link to="/">
                                <span><img src="https://placehold.co/240x70/transparent/000000/png?text=ProjectAlpha&fontSize=34" alt="ProjectAlpha" height="50"></span>
                            </router-link>
                        </div>

                        <div class="card-body p-4">

                            <div class="text-center w-75 m-auto">
                                <h4 class="text-dark-50 text-center mt-0 fw-bold">Free Sign Up</h4>
                                <p class="text-muted mb-4">Don't have an account? Create your account, it takes less than a
                                    minute </p>
                            </div>

                            <b-form @submit.prevent="register">

                                <div v-if="error" class="text-danger text-center mb-2">
                                    {{ errorMessage || 'Please enter valid details' }}
                                </div>
                                <div v-if="loading" class="text-center mb-2">
                                    <b-spinner small variant="primary"></b-spinner> Creating account...
                                </div>

                                <b-form-group label="First Name" label-for="firstname" class="mb-3">
                                    <b-form-input type="text" v-model="first_name" id="firstname" placeholder="Enter your first name" required />
                                </b-form-group>

                                <b-form-group label="Last Name" label-for="lastname" class="mb-3">
                                    <b-form-input type="text" v-model="last_name" id="lastname" placeholder="Enter your last name" required />
                                </b-form-group>

                                <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                                    <b-form-input type="email" v-model="email" id="emailaddress" placeholder="Enter your email" required />
                                </b-form-group>

                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <div class="input-group input-group-merge">
                                        <b-form-input type="password" v-model="password" id="password" placeholder="Enter your password (min 8 characters)" required />
                                        <div class="input-group-text" data-password="false">
                                            <span class="password-eye"></span>
                                        </div>
                                    </div>
                                </div>

                                <div class="mb-3">
                                    <b-form-checkbox id="checkbox-signup">
                                        I accept <a href="#" class="text-muted">Terms and Conditions</a>
                                    </b-form-checkbox>
                                </div>

                                <div class="mb-3 text-center">
                                    <b-button variant="primary" type="submit"> Sign Up</b-button>
                                </div>

                            </b-form>
                        </div> <!-- end card-body -->
                    </div>
                    <!-- end card -->

                    <b-row class="mt-3">
                        <b-col cols="12" class="text-center">
                            <p class="text-muted">Already have account?
                                <router-link to="/login" class="text-muted ms-1"><b>Log In</b></router-link>
                            </p>
                        </b-col> <!-- end col-->
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
// Import our custom Django auth store instead of fake auth
// Using the real Django backend for user registration
import { useDjangoAuthStore } from "@/stores/djangoAuth";
import router from "@/router";
import DefaultLayout from '@/components/layouts/default-layout.vue';
import Footer2 from '@/components/layouts/partials/footer-2.vue';

export default {
    components: { Footer2, DefaultLayout },
    data() {
        return {
            // Use our Django auth store for real authentication
            djangoAuth: useDjangoAuthStore(),
            first_name: '',
            last_name: '',
            email: '',
            password: '',
            error: false,
            errorMessage: '',
            loading: false
        }
    },
    methods: {
        /**
         * Register a new user using the Django backend API
         * Calls the /api/auth/register/ endpoint with user details
         * On success, automatically logs in the user and redirects to home
         */
        async register() {
            // Reset error state
            this.error = false;
            this.errorMessage = '';
            this.loading = true;
            
            try {
                // Call Django backend register endpoint
                await this.djangoAuth.register(
                    this.first_name,
                    this.last_name,
                    this.email,
                    this.password
                );
                
                // Registration successful, redirect to home page
                this.loading = false;
                return router.push('/');
            } catch (error) {
                // Display error message from backend
                this.error = true;
                this.errorMessage = this.djangoAuth.error || 'Registration failed. Please try again.';
                this.loading = false;
            }
        }
    }
}
</script>
