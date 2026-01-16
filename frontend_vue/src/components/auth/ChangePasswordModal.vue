<template>
  <!-- Password Change Modal -->
  <!-- Used for initial password change when user logs in with temporary password -->
  <!-- Docs: https://bootstrap-vue-next.github.io/bootstrap-vue-next/docs/components/modal -->
  <b-modal
    v-model="showModal"
    title="Change Your Password"
    title-class="h4"
    size="md"
    :hide-footer="false"
    :no-close-on-backdrop="true"
    :no-close-on-esc="true"
    :hide-header-close="true"
    @hidden="onModalHidden"
  >
    <!-- Modal Body -->
    <div class="mb-3">
      <!-- Info message explaining why password change is required -->
      <div class="alert alert-info mb-4" role="alert">
        <i class="mdi mdi-information-outline me-2"></i>
        <strong>Password Change Required</strong>
        <p class="mb-0 mt-2">You are using a temporary password. Please change it to a secure password of your choice.</p>
      </div>

      <!-- Password change form -->
      <b-form @submit.prevent="handleChangePassword">
        <!-- Current Password Field -->
        <b-form-group 
          label="Current Password" 
          label-for="current-password"
          class="mb-3"
        >
          <b-form-input
            id="current-password"
            v-model="form.currentPassword"
            type="password"
            placeholder="Enter your current password"
            required
            :state="validationState.currentPassword"
            autocomplete="current-password"
          />
          <b-form-invalid-feedback v-if="errors.currentPassword">
            {{ errors.currentPassword }}
          </b-form-invalid-feedback>
        </b-form-group>

        <!-- New Password Field -->
        <b-form-group 
          label="New Password" 
          label-for="new-password"
          class="mb-3"
        >
          <b-form-input
            id="new-password"
            v-model="form.newPassword"
            type="password"
            placeholder="Enter your new password (min. 8 characters)"
            required
            :state="validationState.newPassword"
            autocomplete="new-password"
            minlength="8"
          />
          <b-form-invalid-feedback v-if="errors.newPassword">
            {{ errors.newPassword }}
          </b-form-invalid-feedback>
          <b-form-text>
            Password must be at least 8 characters long
          </b-form-text>
        </b-form-group>

        <!-- Confirm New Password Field -->
        <b-form-group 
          label="Confirm New Password" 
          label-for="confirm-password"
          class="mb-3"
        >
          <b-form-input
            id="confirm-password"
            v-model="form.confirmPassword"
            type="password"
            placeholder="Confirm your new password"
            required
            :state="validationState.confirmPassword"
            autocomplete="new-password"
            minlength="8"
          />
          <b-form-invalid-feedback v-if="errors.confirmPassword">
            {{ errors.confirmPassword }}
          </b-form-invalid-feedback>
        </b-form-group>

        <!-- Error message display -->
        <div v-if="errorMessage" class="alert alert-danger mb-3" role="alert">
          <i class="mdi mdi-alert-circle-outline me-2"></i>
          {{ errorMessage }}
        </div>
      </b-form>
    </div>

    <!-- Modal Footer -->
    <template #footer>
      <div class="w-100 d-flex justify-content-end gap-2">
        <!-- Change Password Button -->
        <b-button
          variant="primary"
          :disabled="loading || !isFormValid"
          @click="handleChangePassword"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          <i v-else class="mdi mdi-key-change me-2"></i>
          {{ loading ? 'Changing Password...' : 'Change Password' }}
        </b-button>
      </div>
    </template>
  </b-modal>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useDjangoAuthStore } from '@/stores/djangoAuth';

export default defineComponent({
  name: 'ChangePasswordModal',
  props: {
    // Control modal visibility from parent
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'password-changed'],
  data() {
    return {
      // Form data for password change
      form: {
        currentPassword: '', // Current/temporary password
        newPassword: '', // New password user wants to set
        confirmPassword: '' // Confirmation of new password
      },
      // Validation state for form fields
      validationState: {
        currentPassword: null as boolean | null,
        newPassword: null as boolean | null,
        confirmPassword: null as boolean | null
      },
      // Error messages for each field
      errors: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      // General error message from API
      errorMessage: '',
      // Loading state during password change
      loading: false,
      // Reference to Django auth store
      djangoAuth: useDjangoAuthStore()
    };
  },
  computed: {
    // Computed property to control modal visibility
    showModal: {
      get(): boolean {
        return this.modelValue;
      },
      set(value: boolean) {
        this.$emit('update:modelValue', value);
      }
    },
    // Check if form is valid and ready to submit
    isFormValid(): boolean {
      return (
        this.form.currentPassword.length > 0 &&
        this.form.newPassword.length >= 8 &&
        this.form.confirmPassword.length >= 8 &&
        this.form.newPassword === this.form.confirmPassword
      );
    }
  },
  watch: {
    // Watch for changes in new password to validate confirmation
    'form.newPassword'() {
      this.validateNewPassword();
      this.validateConfirmPassword();
    },
    // Watch for changes in confirm password to validate match
    'form.confirmPassword'() {
      this.validateConfirmPassword();
    }
  },
  methods: {
    /**
     * Validate new password field
     * Checks minimum length requirement
     */
    validateNewPassword() {
      if (this.form.newPassword.length === 0) {
        this.validationState.newPassword = null;
        this.errors.newPassword = '';
        return;
      }
      
      if (this.form.newPassword.length < 8) {
        this.validationState.newPassword = false;
        this.errors.newPassword = 'Password must be at least 8 characters long';
      } else {
        this.validationState.newPassword = true;
        this.errors.newPassword = '';
      }
    },

    /**
     * Validate confirm password field
     * Checks if it matches the new password
     */
    validateConfirmPassword() {
      if (this.form.confirmPassword.length === 0) {
        this.validationState.confirmPassword = null;
        this.errors.confirmPassword = '';
        return;
      }
      
      if (this.form.confirmPassword !== this.form.newPassword) {
        this.validationState.confirmPassword = false;
        this.errors.confirmPassword = 'Passwords do not match';
      } else {
        this.validationState.confirmPassword = true;
        this.errors.confirmPassword = '';
      }
    },

    /**
     * Handle password change form submission
     * Validates form and calls API to change password
     */
    async handleChangePassword() {
      // Clear previous errors
      this.errorMessage = '';
      this.errors = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      
      // Validate all fields
      this.validateNewPassword();
      this.validateConfirmPassword();
      
      // Check if form is valid
      if (!this.isFormValid) {
        if (this.form.newPassword.length < 8) {
          this.errors.newPassword = 'Password must be at least 8 characters long';
        }
        if (this.form.confirmPassword !== this.form.newPassword) {
          this.errors.confirmPassword = 'Passwords do not match';
        }
        return;
      }
      
      // Set loading state
      this.loading = true;
      
      try {
        // Call auth store method to change password
        await this.djangoAuth.changePassword(
          this.form.currentPassword,
          this.form.newPassword
        );
        
        // Password changed successfully
        // Emit event to parent component
        this.$emit('password-changed');
        
        // Close modal
        this.showModal = false;
        
        // Reset form
        this.resetForm();
      } catch (error: any) {
        // Handle error from API
        const errorMsg = error.response?.data?.error || 'Failed to change password. Please try again.';
        this.errorMessage = errorMsg;
        
        // If error mentions current password, highlight that field
        if (errorMsg.toLowerCase().includes('current password') || 
            errorMsg.toLowerCase().includes('incorrect')) {
          this.validationState.currentPassword = false;
          this.errors.currentPassword = errorMsg;
        }
      } finally {
        // Clear loading state
        this.loading = false;
      }
    },

    /**
     * Reset form to initial state
     * Called after successful password change or modal close
     */
    resetForm() {
      this.form = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      this.validationState = {
        currentPassword: null,
        newPassword: null,
        confirmPassword: null
      };
      this.errors = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      };
      this.errorMessage = '';
    },

    /**
     * Handle modal hidden event
     * Reset form when modal is closed
     */
    onModalHidden() {
      this.resetForm();
    }
  }
});
</script>

<style scoped>
/* Component-specific styles if needed */
.alert {
  font-size: 0.875rem;
}
</style>
