import { defineStore } from "pinia";
import axios from "axios";
import { useStorage } from "@vueuse/core";

// Define user interface for TypeScript type checking
interface UserProfile {
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
}

// Configure axios defaults for Django backend
axios.defaults.baseURL = 'http://localhost:8000'; // Django backend URL
axios.defaults.headers.common['Content-Type'] = 'application/json';

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
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Token ${this.token}`;
      } else {
        delete axios.defaults.headers.common['Authorization'];
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
        const res = await axios.get('/api/auth/user/');
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
        const res = await axios.post('/api/auth/register/', {
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
     * Login user
     * @param email User's email
     * @param password User's password
     * @returns User data including token
     */
    async logIn(email: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        const res = await axios.post('/api/auth/login/', { email, password });
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
          await axios.post('/api/auth/logout/');
        } catch (error) {
          console.error('Logout error:', error);
          // Continue with logout even if API call fails
        }
      }
      
      // Clear auth data
      this.authUser = null;
      this.token = null;
      this.error = null;
      delete axios.defaults.headers.common['Authorization'];
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
        const res = await axios.put('/api/auth/user/', userData);
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
