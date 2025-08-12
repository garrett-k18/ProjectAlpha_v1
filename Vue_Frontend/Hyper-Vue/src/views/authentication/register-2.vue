<template>
<DefaultLayout body-class="authentication-bg pb-0">
    <div class="auth-fluid">
        <!--Auth fluid left content -->
        <div class="auth-fluid-form-box">
            <div class="card-body d-flex flex-column h-100 gap-3">

                <!-- Logo -->
                <div class="auth-brand text-center text-lg-start">
                    <router-link to="/" class="logo-dark">
                        <span><img src="@/assets/images/logo-dark.png" alt="dark logo" height="22"></span>
                    </router-link>
                    <router-link to="/" class="logo-light">
                        <span><img src="@/assets/images/logo.png" alt="logo" height="22"></span>
                    </router-link>
                </div>

                <div class="my-auto">
                    <!-- title-->
                    <h4 class="mt-3">Free Sign Up</h4>
                    <p class="text-muted mb-4">Don't have an account? Create your account, it takes less than a minute</p>

                    <!-- form -->
                    <b-form action="#">
                        <b-form-group label="Full Name" label-for="fullname" class="mb-3">
                            <b-form-input type="text" id="fullname" placeholder="Enter your name" required />
                        </b-form-group>
                        <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                            <b-form-input type="email" id="emailaddress" required placeholder="Enter your email" />
                        </b-form-group>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <b-form-input type="password" required id="password" placeholder="Enter your password" />
                        </div>
                        <div class="mb-3">

                                <b-form-checkbox id="checkbox-signup">
                                    I accept <a href="javascript: void(0);" class="text-muted">Terms and Conditions</a>
                                </b-form-checkbox>

                        </div>
                        <div class="mb-0 d-grid text-center">
                            <b-button variant="primary" type="submit"><i class="mdi mdi-account-circle"></i> Sign Up </b-button>
                        </div>
                        <!-- social-->
                        <div class="text-center mt-4">
                            <p class="text-muted font-16">Sign up using</p>
                            <ul class="social-list list-inline mt-3">
                                <li class="list-inline-item">
                                    <a href="javascript: void(0);" class="social-list-item border-primary text-primary"><i class="mdi mdi-facebook"></i></a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="javascript: void(0);" class="social-list-item border-danger text-danger"><i class="mdi mdi-google"></i></a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="javascript: void(0);" class="social-list-item border-info text-info"><i class="mdi mdi-twitter"></i></a>
                                </li>
                                <li class="list-inline-item">
                                    <a href="javascript: void(0);" class="social-list-item border-secondary text-secondary"><i class="mdi mdi-github"></i></a>
                                </li>
                            </ul>
                        </div>
                    </b-form>
                    <!-- end form-->
                </div>

                <!-- Footer-->
                <footer class="footer footer-alt">
                    <p class="text-muted">Already have account? <router-link to="/login-2" class="text-muted ms-1"><b>Log In</b></router-link>
                    </p>
                </footer>

            </div> <!-- end .card-body -->
        </div>
        <!-- end auth-fluid-form-box-->

        <!-- Auth fluid right content -->
        <div class="auth-fluid-right text-center">
            <div class="auth-user-testimonial">
                <h2 class="mb-3">I love the color!</h2>
                <p class="lead"><i class="mdi mdi-format-quote-open"></i> It's a elegent templete. I love it very much! . <i class="mdi mdi-format-quote-close"></i>
                </p>
                <p>
                    - Hyper Admin User
                </p>
            </div> <!-- end auth-user-testimonial-->
        </div>
        <!-- end Auth fluid right content -->
    </div>
    <!-- end auth-fluid-->
</DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from '@/components/layouts/default-layout.vue';
export default {
    components: { DefaultLayout },

}
</script>
