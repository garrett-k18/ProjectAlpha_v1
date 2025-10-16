// Shared Google Maps JS API loader using @googlemaps/js-api-loader
// This centralizes loading, enables specifying libraries (e.g., 'marker', 'places'),
// and avoids direct <script> usage so we can follow Google's async loading guidance.

import { Loader } from '@googlemaps/js-api-loader'

// Read from Vite env
const apiKey = (import.meta as any).env.VITE_GOOGLE_MAPS_API_KEY as string | undefined

// Determine whether the environment actually supplied a key; trim to catch whitespace-only entries.
const hasApiKey = typeof apiKey === 'string' && apiKey.trim().length > 0

if (!hasApiKey) {
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
const loader = hasApiKey
  ? new Loader({
      apiKey: apiKey!.trim(),
      version: 'weekly',
      libraries: libraries as any,
      id: 'gmap-script',
    })
  : null

// Expose a single promise for the app to reuse. When the API key is missing, resolve immediately so
// downstream consumers can branch on a falsy value without the loader throwing an exception.
export const googleApiPromise: Promise<any> = loader ? loader.load() : Promise.resolve(null)
