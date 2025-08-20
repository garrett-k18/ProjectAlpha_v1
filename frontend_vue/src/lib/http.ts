// src/lib/http.ts
// Centralized Axios instance for API calls
// - baseURL comes from Vite env (VITE_API_BASE_URL)
// - falls back to "/api" so Vite dev proxy forwards to Django
// Docs reviewed:
// * Vite Env & Mode: https://vitejs.dev/guide/env-and-mode.html
// * Vite server proxy: https://vitejs.dev/config/server-options.html#server-proxy
// * Axios Instances: https://axios-http.com/docs/instance

import axios from 'axios';

// Create an Axios instance so we avoid global defaults and keep things modular
const http = axios.create({
  // In dev, set VITE_API_BASE_URL=/api so requests go to Vite and are proxied to Django
  // In prod, set VITE_API_BASE_URL to your public backend URL (e.g., https://api.example.com)
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    // Ensure JSON by default
    'Content-Type': 'application/json',
  },
  // Keep credentials enabled to support session-based endpoints when needed
  withCredentials: true,
});

// Inject Authorization header from localStorage on each request as a safety net.
// Rationale:
// - Pinia store sets http.defaults.headers on startup, but component race conditions
//   can still trigger before that runs. This interceptor ensures the token is present.
// - DRF TokenAuthentication expects: Authorization: "Token <token>"
// Docs reviewed:
// * Axios Interceptors: https://axios-http.com/docs/interceptors
// * DRF TokenAuthentication: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
http.interceptors.request.use((config) => {
  try {
    // Only inject if not already set explicitly
    const hasAuth = !!(config.headers && (config.headers as any)['Authorization'])
    if (!hasAuth) {
      const token = localStorage.getItem('djangoAuthToken')
      if (token) {
        // Ensure headers object exists
        config.headers = config.headers || {}
        ;(config.headers as any)['Authorization'] = `Token ${token}`
      }
    }
  } catch (e) {
    // Non-fatal: continue without token
    console.warn('[http] Authorization injection skipped:', e)
  }
  return config
})

export default http;
