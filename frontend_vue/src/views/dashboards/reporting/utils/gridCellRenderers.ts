/**
 * AG Grid Custom Cell Renderers for Reporting Dashboard
 * 
 * WHAT: Reusable cell renderer functions for common data types
 * WHY: Consistent formatting across all grids (currency, percentages, badges, dates)
 * WHERE: Used in column definitions across all report views
 * 
 * FEATURES:
 * - Currency formatting with M/k suffixes
 * - Percentage formatting with color coding
 * - Status badges with appropriate colors
 * - LTV ratio with risk-based colors
 * - Date formatting
 * - Number formatting with commas
 */

import type { ICellRendererParams } from 'ag-grid-community'

/**
 * WHAT: Format number as currency
 * WHY: Display dollar amounts in readable format ($1.5MM, $250k, $1,234)
 * 
 * @param value - Number value to format
 * @param precision - Decimal places (default: 1 for millions/thousands, 0 for small amounts)
 * @returns Formatted currency string
 */
export function formatCurrency(value: number | null | undefined, precision: number = 1): string {
  if (value === null || value === undefined || isNaN(value)) return '-'
  
  const abs = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  
  if (abs >= 1_000_000) {
    return `${sign}$${(abs / 1_000_000).toFixed(precision)}MM`
  }
  if (abs >= 1_000) {
    return `${sign}$${(abs / 1_000).toFixed(precision)}k`
  }
  return `${sign}$${abs.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
}

/**
 * WHAT: Currency cell renderer for AG Grid
 * WHY: Display currency in grid cells with proper formatting
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function currencyRenderer(params: ICellRendererParams): string {
  return `<span class="fw-semibold">${formatCurrency(params.value)}</span>`
}

/**
 * WHAT: Format number as percentage
 * WHY: Display ratios and percentages with % sign
 * 
 * @param value - Number value (0-100 or 0-1 depending on source)
 * @param decimals - Decimal places (default: 1)
 * @param isDecimal - True if value is 0-1 (e.g., 0.85 = 85%), false if already 0-100
 * @returns Formatted percentage string
 */
export function formatPercent(value: number | null | undefined, decimals: number = 1, isDecimal: boolean = false): string {
  if (value === null || value === undefined || isNaN(value)) return '-'
  
  const pct = isDecimal ? value * 100 : value
  return `${pct.toFixed(decimals)}%`
}

/**
 * WHAT: Percentage cell renderer
 * WHY: Display percentages with color coding
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function percentRenderer(params: ICellRendererParams): string {
  if (params.value === null || params.value === undefined) return '-'
  return `<span>${formatPercent(params.value)}</span>`
}

/**
 * WHAT: LTV (Loan-to-Value) cell renderer
 * WHY: Color-code LTV ratios by risk level
 * 
 * LOGIC:
 * - Green: < 90% (healthy)
 * - Yellow: 90-100% (monitor)
 * - Red: > 100% (high risk)
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function ltvRenderer(params: ICellRendererParams): string {
  const value = params.value
  if (value === null || value === undefined || isNaN(value)) return '-'
  
  let colorClass = 'text-success'
  if (value > 100) {
    colorClass = 'text-danger fw-bold'
  } else if (value >= 90) {
    colorClass = 'text-warning fw-semibold'
  }
  
  return `<span class="${colorClass}">${formatPercent(value)}</span>`
}

/**
 * WHAT: Status badge cell renderer
 * WHY: Display status with colored badges matching Hyper UI theme
 * 
 * STATUS COLOR MAPPING:
 * - DD (Due Diligence): Info (blue)
 * - AWARDED: Success (green)
 * - PASS: Secondary (gray)
 * - BOARD: Primary (blue)
 * - PENDING: Warning (yellow)
 * - CLOSED: Dark
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function statusBadgeRenderer(params: ICellRendererParams): string {
  const status = params.value
  if (!status) return '-'
  
  const statusMap: Record<string, { class: string; label: string }> = {
    'DD': { class: 'bg-info', label: 'Due Diligence' },
    'AWARDED': { class: 'bg-success', label: 'Awarded' },
    'PASS': { class: 'bg-secondary', label: 'Pass' },
    'BOARD': { class: 'bg-primary', label: 'Board Review' },
    'PENDING': { class: 'bg-warning', label: 'Pending' },
    'CLOSED': { class: 'bg-dark', label: 'Closed' },
  }
  
  const config = statusMap[status.toUpperCase()] || { class: 'bg-secondary', label: status }
  
  return `<span class="badge ${config.class}">${config.label}</span>`
}

/**
 * WHAT: Number formatter with commas
 * WHY: Display large counts (asset count, etc.) with thousands separators
 * 
 * @param value - Number value
 * @returns Formatted string with commas
 */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return value.toLocaleString('en-US')
}

/**
 * WHAT: Number cell renderer
 * WHY: Display formatted numbers in grid
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function numberRenderer(params: ICellRendererParams): string {
  return `<span>${formatNumber(params.value)}</span>`
}

/**
 * WHAT: Date formatter
 * WHY: Display dates in consistent format (MM/DD/YYYY)
 * 
 * @param value - Date string or Date object
 * @returns Formatted date string
 */
export function formatDate(value: string | Date | null | undefined): string {
  if (!value) return '-'
  
  try {
    const date = typeof value === 'string' ? new Date(value) : value
    return date.toLocaleDateString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric',
    })
  } catch (error) {
    console.error('[GridCellRenderer] Invalid date:', value, error)
    return '-'
  }
}

/**
 * WHAT: Date cell renderer
 * WHY: Display formatted dates in grid
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function dateRenderer(params: ICellRendererParams): string {
  return `<span class="text-muted">${formatDate(params.value)}</span>`
}

/**
 * WHAT: Action buttons cell renderer
 * WHY: Add action buttons (View, Edit, Delete) to grid rows
 * 
 * NOTE: Use sparingly - prefer row click for primary action
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function actionButtonsRenderer(params: ICellRendererParams): string {
  return `
    <div class="d-flex gap-1 justify-content-center">
      <button 
        class="btn btn-sm btn-outline-primary ag-action-btn" 
        data-action="view" 
        data-id="${params.data?.id || ''}"
        title="View Details"
      >
        <i class="mdi mdi-eye"></i>
      </button>
    </div>
  `
}

/**
 * WHAT: Boolean (Yes/No) cell renderer
 * WHY: Display checkmarks or X marks for boolean values
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function booleanRenderer(params: ICellRendererParams): string {
  if (params.value === null || params.value === undefined) return '-'
  
  const isTrue = params.value === true || params.value === 'true' || params.value === 1
  
  if (isTrue) {
    return '<i class="mdi mdi-check-circle text-success fs-5"></i>'
  }
  return '<i class="mdi mdi-close-circle text-danger fs-5"></i>'
}

/**
 * WHAT: Link cell renderer
 * WHY: Display clickable links in grid cells
 * 
 * @param params - AG Grid cell renderer params
 * @param urlField - Field name containing the URL (optional)
 * @returns HTML string for cell
 */
export function linkRenderer(params: ICellRendererParams, urlField?: string): string {
  const text = params.value
  const url = urlField ? params.data?.[urlField] : '#'
  
  if (!text) return '-'
  
  return `<a href="${url}" class="text-primary" target="_blank" rel="noopener noreferrer">
    ${text} <i class="mdi mdi-open-in-new"></i>
  </a>`
}

/**
 * WHAT: Risk level badge renderer
 * WHY: Display risk levels (Low, Medium, High, Critical) with color coding
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function riskLevelRenderer(params: ICellRendererParams): string {
  const risk = params.value?.toLowerCase()
  
  const riskMap: Record<string, { class: string; label: string }> = {
    'low': { class: 'bg-success-lighten text-success', label: 'Low' },
    'medium': { class: 'bg-warning-lighten text-warning', label: 'Medium' },
    'high': { class: 'bg-danger-lighten text-danger', label: 'High' },
    'critical': { class: 'bg-danger', label: 'Critical' },
  }
  
  const config = riskMap[risk] || { class: 'bg-secondary', label: risk || '-' }
  
  return `<span class="badge ${config.class}">${config.label}</span>`
}

/**
 * WHAT: Property type icon renderer
 * WHY: Display property type icons (SFR, Condo, Multi-family, etc.)
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function propertyTypeRenderer(params: ICellRendererParams): string {
  const type = params.value?.toUpperCase()
  
  const typeMap: Record<string, { icon: string; label: string }> = {
    'SFR': { icon: 'mdi-home', label: 'Single Family' },
    'CONDO': { icon: 'mdi-office-building', label: 'Condo' },
    'MULTI': { icon: 'mdi-domain', label: 'Multi-family' },
    'COMMERCIAL': { icon: 'mdi-store', label: 'Commercial' },
  }
  
  const config = typeMap[type] || { icon: 'mdi-help-circle', label: type || '-' }
  
  return `
    <div class="d-flex align-items-center gap-2">
      <i class="mdi ${config.icon} text-muted"></i>
      <span>${config.label}</span>
    </div>
  `
}

/**
 * WHAT: Delinquency days renderer
 * WHY: Color-code delinquency days by severity
 * 
 * LOGIC:
 * - Green: 0 days (current)
 * - Yellow: 1-30 days
 * - Orange: 31-60 days
 * - Red: 60+ days
 * 
 * @param params - AG Grid cell renderer params
 * @returns HTML string for cell
 */
export function delinquencyRenderer(params: ICellRendererParams): string {
  const days = params.value
  if (days === null || days === undefined) return '-'
  
  let colorClass = 'text-success'
  if (days === 0) {
    return '<span class="badge bg-success-lighten text-success">Current</span>'
  } else if (days <= 30) {
    colorClass = 'text-warning'
  } else if (days <= 60) {
    colorClass = 'text-danger'
  } else {
    colorClass = 'text-danger fw-bold'
  }
  
  return `<span class="${colorClass}">${days} days</span>`
}

