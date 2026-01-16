import { defineStore } from "pinia";
// Use centralized Axios instance instead of global axios defaults
// Docs: Axios Instances https://axios-http.com/docs/instance
// This instance reads baseURL from Vite env (set in .env files)
import http from "@/lib/http";
import { useStorage } from "@vueuse/core";

// Define user interface for TypeScript type checking
export interface UserProfile {
  user_id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  job_title?: string;
  department?: string;
  phone_number?: string;
  access_level: number;
  theme_preference: string;
  notification_enabled: boolean;
  profile_picture?: string;
  must_change_password?: boolean; // Flag indicating if user must change password
}

// Note:
// We intentionally do NOT set global axios defaults.
// All requests below use the http instance which points to VITE_API_BASE_URL (or "/api").

/**
 * Django Authentication Store
 * Handles authentication with Django backend using REST API
 * Stores user data and token in localStorage
 */
export const useDjangoAuthStore = defineStore("djangoAuth", {
  state: () => ({
    // Store user data and token in localStorage via useStorage
    authUser: useStorage<UserProfile | null>('djangoAuthUser', null),
    token: useStorage<string | null>('djangoAuthToken', null),
    loading: false,
    error: null as string | null
  }),

  getters: {
    // Get current user
    user: (state) => state.authUser,
    
    // Check if user is authenticated
    isAuthenticated: (state) => !!state.token,
    
    // Check if user is admin (superuser)
    isAdmin: (state) => state.authUser?.is_superuser || false,
    
    // Get user access level
    accessLevel: (state) => state.authUser?.access_level || 0
  },

  actions: {
    /**
     * Set axios auth header when token changes
     */
    setAuthHeader() {
      // Attach/detach the token to our http instance only
      if (this.token) {
        http.defaults.headers.common['Authorization'] = `Token ${this.token}`;
      } else {
        delete http.defaults.headers.common['Authorization'];
      }
    },

    /**
     * Fetch current user details from backend
     */
    async fetchUser() {
      if (!this.token) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        this.setAuthHeader();
        // Relative path so it works with Vite proxy in dev and env baseURL in prod
        const res = await http.get('/auth/user/');
        this.authUser = res.data;
      } catch (error: any) {
        console.error('Error fetching user:', error);
        this.error = 'Failed to fetch user details';
        // If unauthorized, clear auth data
        if (error.response?.status === 401) {
          this.logout();
        }
      } finally {
        this.loading = false;
      }
    },

    /**
     * Register new user
     * @param first_name User's first name
     * @param last_name User's last name
     * @param email User's email (used as username)
     * @param password User's password
     * @returns User data including token
     */
    async register(first_name: string, last_name: string, email: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        // Fetch CSRF token before registration
        await this.fetchCsrfToken();
        
        const res = await http.post('/auth/register/', {
          first_name,
          last_name,
          email,
          password
        });
        
        this.authUser = res.data;
        this.token = res.data.token;
        this.setAuthHeader();
        return res.data;
      } catch (error: any) {
        console.error('Registration error:', error);
        this.error = error.response?.data?.error || 'Registration failed';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Get CSRF token from Django backend
     * This must be called before making POST requests to set the csrftoken cookie
     * Docs: https://docs.djangoproject.com/en/5.2/ref/csrf/#ajax
     */
    async fetchCsrfToken() {
      try {
        await http.get('/auth/csrf/');
        // Cookie is automatically set by Django, no need to store it
      } catch (error) {
        console.warn('Failed to fetch CSRF token:', error);
        // Non-fatal - continue anyway
      }
    },

    /**
     * Login user
     * @param email User's email
     * @param password User's password
     * @returns User data including token
     */
    async logIn(email: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        // Fetch CSRF token before login
        await this.fetchCsrfToken();
        
        const res = await http.post('/auth/login/', { email, password });
        this.authUser = res.data;
        this.token = res.data.token;
        this.setAuthHeader();
        return res.data;
      } catch (error: any) {
        console.error('Login error:', error);
        this.error = error.response?.data?.error || 'Invalid credentials';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Logout user
     * Calls logout API and clears local auth data
     */
    async logout() {
      if (this.token) {
        try {
          this.setAuthHeader();
          await http.post('/auth/logout/');
        } catch (error) {
          console.error('Logout error:', error);
          // Continue with logout even if API call fails
        }
      }
      
      // Clear auth data
      this.authUser = null;
      this.token = null;
      this.error = null;
      delete http.defaults.headers.common['Authorization'];
    },

    /**
     * Update user profile
     * @param userData Object containing user data to update
     * @returns Response data
     */
    async updateProfile(userData: Partial<UserProfile>) {
      if (!this.token) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        this.setAuthHeader();
        const res = await http.put('/auth/user/', userData);
        // Update only changed fields
        this.authUser = { ...this.authUser as UserProfile, ...userData };
        return res.data;
      } catch (error: any) {
        console.error('Profile update error:', error);
        this.error = error.response?.data?.error || 'Failed to update profile';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Change user password
     * Used for initial password change when must_change_password is true
     * @param oldPassword Current password
     * @param newPassword New password to set
     * @returns Response data
     */
    async changePassword(oldPassword: string, newPassword: string) {
      if (!this.token) {
        throw new Error('Not authenticated');
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        this.setAuthHeader();
        const res = await http.post('/auth/change-password/', {
          old_password: oldPassword,
          new_password: newPassword
        });
        
        // Update must_change_password flag in authUser
        if (this.authUser) {
          this.authUser.must_change_password = false;
        }
        
        return res.data;
      } catch (error: any) {
        console.error('Password change error:', error);
        this.error = error.response?.data?.error || 'Failed to change password';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Initialize auth from stored token
     * Called when app starts to restore authentication state
     */
    async initAuth() {
      if (this.token) {
        await this.fetchUser();
      }
    }
  }
});
