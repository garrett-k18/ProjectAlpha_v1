import { createRouter, createWebHistory } from 'vue-router'
import {allRoutes} from "@/router/routes";
// Import our Django auth store instead of fake auth
import {useDjangoAuthStore} from "@/stores/djangoAuth";

// Flag to bypass authentication in development mode
// Set this to false when you want to re-enable authentication
const BYPASS_AUTH_IN_DEV = true;

// Check if we're in development mode
// In Vite, we use import.meta.env instead of process.env
const isDevelopment = import.meta.env.DEV; // DEV is a boolean that's true in development mode


const router = createRouter({
  // Use empty string as base URL for development
  // In Vite, we use import.meta.env instead of process.env
  history: createWebHistory(import.meta.env.BASE_URL || ''),  // BASE_URL is defined in Vite
  routes: allRoutes,

  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
})

// Before each route evaluates...
router.beforeEach((routeTo, routeFrom, next) => {

  // Check if auth is required on this route
  // (including nested routes).
  const authRequired = routeTo.matched.some((route) => route.meta.authRequired)

  // If auth isn't required for the route, just continue.
  if (!authRequired) return next()
  
  // Check if we're in development mode and bypassing auth
  if (isDevelopment && BYPASS_AUTH_IN_DEV) {
    console.log('Development mode: Bypassing authentication check');
    return next();
  }

  // Use our Django auth store for authentication checks
  let djangoAuth = useDjangoAuthStore()
  // If auth is required and the user is logged in...
  if (djangoAuth.isAuthenticated) {
    return next()
  }

  // If auth is required and the user is NOT currently logged in,
  // redirect to login.
  redirectToLogin()

  function redirectToLogin() {
    // Pass the original route to the login component
    next({ name: 'login', query: { redirectFrom: routeTo.fullPath } })
  }
})

export default router
