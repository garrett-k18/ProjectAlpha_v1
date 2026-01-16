<template>
<DefaultLayout body-class="authentication-bg pb-0">
    <div class="auth-fluid">
        <!--Auth fluid left content -->
        <div class="auth-fluid-form-box">
            <div class="card-body d-flex flex-column h-100 gap-3">

                <!-- Logo -->
                <div class="auth-brand text-center text-lg-start">
                    <router-link to="/home" class="logo-light">
                        <span><img src="@/assets/images/logo.png" alt="logo" height="22"></span>
                    </router-link>
                </div>

                <div class="my-auto">
                    <!-- title-->
                    <h4 class="mt-0">Sign In</h4>
                    <p class="text-muted mb-4">Enter your email address and password to access account.</p>

                    <!-- form -->
                    <b-form @submit.prevent="logIn">
                        <b-form-group label="Email address" label-for="emailaddress" class="mb-3">
                            <b-form-input type="email" id="emailaddress" v-model="email" required placeholder="Enter your email" />
                        </b-form-group>
                        <div class="mb-3">
                            <router-link to="/recoverpw-2" class="text-muted float-end"><small>Forgot your password?</small></router-link>
                            <label for="password" class="form-label">Password</label>
                            <b-form-input type="password" required id="password" v-model="password" placeholder="Enter your password" />
                        </div>
                        <div class="mb-3">
                            <b-form-checkbox-group>
                                <b-form-checkbox id="checkbox-signin" v-model="checked">
                                    Remember me
                                </b-form-checkbox>
                            </b-form-checkbox-group>
                        </div>
                        <div v-if="error" class="alert alert-danger text-center mb-3">
                            {{ errorMessage || 'Please enter valid credentials' }}
                        </div>
                        <div v-if="loading" class="text-center mb-3">
                            <b-spinner small variant="primary"></b-spinner> Logging in...
                        </div>
                        <div class="d-grid mb-0 text-center">
                            <b-button variant="primary" type="submit" :disabled="loading">
                                <i class="mdi mdi-login"></i> {{ loading ? 'Logging in...' : 'Log In' }}
                            </b-button>
                        </div>
                        <!-- Phone Number Sign In Option - To Be Implemented -->
                        <div class="text-center mt-4">
                            <p class="text-muted font-16">Or</p>
                            <b-button variant="outline-primary" class="w-100" disabled>
                                <i class="mdi mdi-phone"></i> Sign In with Phone Number (Coming Soon)
                            </b-button>
                        </div>
                    </b-form>
                    <!-- end form-->
                </div>

                <!-- Footer removed - users must be assigned accounts, no self-registration -->

            </div> <!-- end .card-body -->
        </div>
    </div>
    <!-- end auth-fluid-form-box-->

    <!-- Auth fluid right content -->
    <div class="auth-fluid-right text-center">
        <div class="auth-user-testimonial">
            <!-- Testimonial content removed -->
        </div> <!-- end auth-user-testimonial-->
    </div>
    <!-- end Auth fluid right content -->
</DefaultLayout>
<!-- end auth-fluid-->

<!-- Password Change Modal -->
<!-- Shown when user logs in with temporary password and must_change_password is true -->
<ChangePasswordModal
  v-model="showPasswordChangeModal"
  @password-changed="onPasswordChanged"
/>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import DefaultLayout from '@/components/layouts/default-layout.vue'
import ChangePasswordModal from '@/components/auth/ChangePasswordModal.vue';
import { useDjangoAuthStore } from "@/stores/djangoAuth";
import type { UserProfile } from "@/stores/djangoAuth";
import router from "@/router";

export default defineComponent({
    components: { 
        DefaultLayout,
        ChangePasswordModal
    },
    data() {
        return {
            // Form fields for login
            email: '',
            password: '',
            checked: false,
            // Django auth store reference
            djangoAuth: useDjangoAuthStore(),
            // Error state for login
            error: false,
            errorMessage: '',
            // Loading state for login
            loading: false,
            // Flag to control password change modal visibility
            showPasswordChangeModal: false
        }
    },
    methods: {
        /**
         * Handle user login
         * Checks if password change is required after successful login
         */
        async logIn() {
          // Reset error state
          this.error = false;
          this.errorMessage = '';
          this.loading = true;
          
          try {
            // Use our Django auth store to log in
            const userData = await this.djangoAuth.logIn(this.email, this.password);
            this.loading = false;
            
            // Check if user must change password
            // If must_change_password flag is true, show password change modal instead of redirecting
            if (userData.must_change_password) {
              // Show password change modal
              this.showPasswordChangeModal = true;
              // Don't redirect yet - wait for password change
            } else {
              // Password change not required, proceed with normal redirect
              // After successful login, prefer an explicit redirectFrom target (set by router guard)
              // and fall back to the main homepage dashboard ('/home') as the default.
              const redirectTarget = (this.$route.query.redirectFrom as string) || '/home';
              return router.push(redirectTarget);
            }
          } catch (error) {
            // Handle login error
            this.error = true;
            this.errorMessage = this.djangoAuth.error || 'Login failed';
            this.loading = false;
          }
        },

        /**
         * Handle password change completion
         * Called when user successfully changes their password
         * Redirects to home page after password change
         */
        onPasswordChanged() {
          // Password changed successfully
          // Close the modal
          this.showPasswordChangeModal = false;
          
          // Redirect to home page
          // After password change, prefer an explicit redirectFrom target (set by router guard)
          // and fall back to the main homepage dashboard ('/home') as the default.
          const redirectTarget = (this.$route.query.redirectFrom as string) || '/home';
          router.push(redirectTarget);
        }
    }
});
</script>
