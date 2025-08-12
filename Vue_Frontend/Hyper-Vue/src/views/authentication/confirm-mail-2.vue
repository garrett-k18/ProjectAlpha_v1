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
                    <!-- email send icon with text-->
                    <div class="text-center m-auto">
                        <img src="@/assets/images/svg/mail_sent.svg" alt="mail sent image" height="64" />
                        <h4 class="text-dark-50 text-center mt-4 fw-bold">Please check your email</h4>
                        <p class="text-muted mb-4">
                            A email has been send to <b>youremail@domain.com</b>.
                            Please check for an email from company and click on the included link to
                            reset your password.
                        </p>
                    </div>

                    <!-- form -->
                    <b-form @click="Replace">
                        <div class="mb-0 d-grid text-center">
                            <b-button variant="primary" type="submit"><i class="mdi mdi-home me-1"></i> Back to Home</b-button>
                        </div>
                    </b-form>
                    <!-- end form-->
                </div>

                <!-- Footer-->
                <Footer2 />

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
import DefaultLayout from "@/components/layouts/default-layout.vue";
import Footer2 from "@/components/layouts/partials/footer-2.vue";

export default {
    components: { Footer2, DefaultLayout },
    methods: {
        Replace() {
            this.$router.push("/");
        }
    },
}
</script>
