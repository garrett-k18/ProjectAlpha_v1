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
                    <h4 class="mt-0">Sign In</h4>
                    <p class="text-muted mb-4">Enter your email address and password to access account.</p>

                    <!-- form -->
                    <b-form action="#">
                        <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                            <b-form-input type="email" id="emailaddress" required placeholder="Enter your email" />
                        </b-form-group>
                        <div class="mb-3">
                            <router-link to="/recoverpw-2" class="text-muted float-end"><small>Forgot your password?</small></router-link>
                            <label for="password" class="form-label">Password</label>
                            <b-form-input type="password" required id="password" placeholder="Enter your password" />
                        </div>
                        <div class="mb-3">
                            <b-form-checkbox-group>
                                <b-form-checkbox id="checkbox-signin">
                                    Remember me
                                </b-form-checkbox>
                            </b-form-checkbox-group>
                        </div>
                        <div class="d-grid mb-0 text-center">
                            <b-button variant="primary" type="submit"><i class="mdi mdi-login"></i> Log In </b-button>
                        </div>
                        <!-- social-->
                        <div class="text-center mt-4">
                            <p class="text-muted font-16">Sign in with</p>
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
                    <p class="text-muted">Don't have an account? <router-link to="/register-2" class="text-muted ms-1"><b>Sign Up</b></router-link>
                    </p>
                </footer>

            </div> <!-- end .card-body -->
        </div>
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
</DefaultLayout>
<!-- end auth-fluid-->
</template>

<script>
import DefaultLayout from '@/components/layouts/default-layout.vue'
export default {
    components: { DefaultLayout },
}
</script>
