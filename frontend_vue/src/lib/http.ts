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
  // Prevent indefinitely pending requests from locking UI during dev
  timeout: 20000,
});

// Helper function to get CSRF token from cookies
// Django sets csrftoken cookie which we need to send back in X-CSRFToken header
// Docs: https://docs.djangoproject.com/en/5.2/ref/csrf/#ajax
function getCsrfToken(): string | null {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
}

// Request interceptor: inject Authorization token and CSRF token
// Rationale:
// - Pinia store sets http.defaults.headers on startup, but component race conditions
//   can still trigger before that runs. This interceptor ensures tokens are present.
// - DRF TokenAuthentication expects: Authorization: "Token <token>"
// - Django CSRF expects: X-CSRFToken header for POST/PUT/PATCH/DELETE
// Docs reviewed:
// * Axios Interceptors: https://axios-http.com/docs/interceptors
// * DRF TokenAuthentication: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
// * Django CSRF with AJAX: https://docs.djangoproject.com/en/5.2/ref/csrf/#ajax
http.interceptors.request.use((config) => {
  try {
    // Ensure headers object exists
    config.headers = config.headers || {};
    
    // Inject CSRF token for non-safe methods
    const csrfToken = getCsrfToken();
    if (csrfToken && config.method && !['get', 'head', 'options'].includes(config.method.toLowerCase())) {
      (config.headers as any)['X-CSRFToken'] = csrfToken;
    }
    
    // Inject Authorization token if not already set
    const hasAuth = !!(config.headers && (config.headers as any)['Authorization']);
    if (!hasAuth) {
      const token = localStorage.getItem('djangoAuthToken');
      if (token) {
        (config.headers as any)['Authorization'] = `Token ${token}`;
      }
    }
  } catch (e) {
    // Non-fatal: continue without tokens
    console.warn('[http] Token injection skipped:', e);
  }
  return config;
})

export default http;
