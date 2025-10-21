import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/',
  plugins: [
    vue(),
  ],
  // Dev server proxy: forward /api requests to Django backend
  // Docs: https://vitejs.dev/config/server-options.html#server-proxy
  server: {
    // Listen on all interfaces so the app is reachable from other devices on LAN
    // Docs: https://vitejs.dev/config/server-options.html#server-host
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Django dev server
        changeOrigin: true,
        secure: false,
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
