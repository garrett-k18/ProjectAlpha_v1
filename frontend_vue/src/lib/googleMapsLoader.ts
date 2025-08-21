// Shared Google Maps JS API loader using @googlemaps/js-api-loader
// This centralizes loading, enables specifying libraries (e.g., 'marker', 'places'),
// and avoids direct <script> usage so we can follow Google's async loading guidance.

import { Loader } from '@googlemaps/js-api-loader'

// Read from Vite env
const apiKey = (import.meta as any).env.VITE_GOOGLE_MAPS_API_KEY as string | undefined
if (!apiKey) {
  // eslint-disable-next-line no-console
  console.warn('[googleMapsLoader] Missing VITE_GOOGLE_MAPS_API_KEY; Google Maps features will be disabled.')
}

// Allow override of libraries via env, default to 'places,marker' per current needs
const libsEnv = ((import.meta as any).env.VITE_GOOGLE_MAPS_LIBRARIES as string) || 'places,marker'
const libraries = libsEnv
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean) as string[]

// Optional: you can set language/region by adding more loader options if needed
const loader = new Loader({
  apiKey: apiKey || '',
  version: 'weekly',
  libraries: libraries as any,
  id: 'gmap-script',
})

// Expose a single promise for the app to reuse
export const googleApiPromise: Promise<any> = loader.load()
