// TypeScript shims for third-party libraries without official @types
// Docs: https://www.typescriptlang.org/docs/handbook/declaration-files/templates/module-d-ts.html

declare module 'vue-the-mask' {
  import type { Plugin } from 'vue'
  const VueTheMask: Plugin
  export default VueTheMask
}

declare module 'jquery' {
  const jQuery: any
  export default jQuery
}

// Augment Window to avoid TS errors when assigning globals in main.ts
declare global {
  interface Window {
    $: any
    jQuery: any
    moment: any
  }
}

export {}
