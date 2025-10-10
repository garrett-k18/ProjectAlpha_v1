/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_GOOGLE_MAPS_API_KEY?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Ambient module declarations for libraries without TypeScript types
declare module 'jsvectormap';
declare module 'jsvectormap/dist/maps/world.js';
