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
                    <h4>Reset Password</h4>
                    <p class="text-muted mb-4">Enter your email address and we'll send you an email with instructions to reset your password.</p>

                    <!-- form -->
                    <b-form action="#">
                        <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                            <b-form-input class="form-control" type="email" id="emailaddress" required="" placeholder="Enter your email" />
                        </b-form-group>
                        <b-form-group class="mb-0 text-center d-grid ">
                            <b-button variant="primary" class="w-100" type="submit"><i class="mdi mdi-lock-reset"></i> Reset Password </b-button>
                        </b-form-group>
                    </b-form>
                    <!-- end form-->
                </div>

                <!-- Footer-->
                <footer class="footer footer-alt">
                    <p class="text-muted">Back to <router-link to="/login-2" class="text-muted ms-1"><b>Log In</b></router-link>
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
</DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from '@/components/layouts/default-layout.vue';
export default {
    components: { DefaultLayout },
}
</script>
