/*
  Global Vue directive: v-currency
  - Live-formats an input as a currency-like integer (commas, no decimals)
  - Keeps only digits in the underlying string
  - Uses Intl.NumberFormat for locale-safe grouping (en-US by default)

  Usage:
    <input v-currency />
    <b-form-input v-currency />

  Notes:
  - This directive formats display only. Your component should still read the
    numeric value by stripping non-digits from event.target.value on @input
    to keep your model as a number.
  - Caret is moved to end after formatting for simplicity; we can refine to
    preserve exact caret position if needed.
*/

import type { Directive } from 'vue'

const nf = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

function sanitizeDigits(val: string): string {
  return (val || '').replace(/[^0-9]/g, '')
}

function formatDigits(digits: string): string {
  if (!digits) return ''
  try {
    return nf.format(Number(digits))
  } catch {
    return digits
  }
}

function applyFormat(el: HTMLInputElement) {
  const digits = sanitizeDigits(el.value)
  const formatted = formatDigits(digits)
  if (el.value !== formatted) {
    el.value = formatted
  }
  try {
    const len = formatted.length
    el.setSelectionRange(len, len)
  } catch {
    // ignore
  }
}

export const currencyDirective: Directive<HTMLInputElement, void> = {
  mounted(el) {
    // If wrapped by BootstrapVueNext, the root el might be a div; seek the real input
    const input: HTMLInputElement | null = (el as any).tagName === 'INPUT' ? (el as HTMLInputElement) : (el.querySelector?.('input') as HTMLInputElement | null)
    const target = input || (el as unknown as HTMLInputElement)

    const onInput = () => applyFormat(target)
    const onBlur = () => applyFormat(target)
    
    // Initial format (in case value was prefilled)
    applyFormat(target)
    
    // Also format after a short delay to catch v-model updates
    setTimeout(() => applyFormat(target), 100)
    
    target.addEventListener('input', onInput)
    target.addEventListener('blur', onBlur)

    // Store cleanup
    ;(target as any)._currency_cleanup = () => {
      target.removeEventListener('input', onInput)
      target.removeEventListener('blur', onBlur)
    }
  },
  updated(el) {
    // Re-apply format when the element updates (e.g., v-model changes)
    const input: HTMLInputElement | null = (el as any).tagName === 'INPUT' ? (el as HTMLInputElement) : (el.querySelector?.('input') as HTMLInputElement | null)
    const target = input || (el as unknown as HTMLInputElement)
    applyFormat(target)
  },
  beforeUnmount(el) {
    const input: HTMLInputElement | null = (el as any).tagName === 'INPUT' ? (el as HTMLInputElement) : (el.querySelector?.('input') as HTMLInputElement | null)
    const target = input || (el as unknown as HTMLInputElement)
    const cleanup = (target as any)._currency_cleanup
    if (cleanup) cleanup()
  },
}

export default currencyDirective
