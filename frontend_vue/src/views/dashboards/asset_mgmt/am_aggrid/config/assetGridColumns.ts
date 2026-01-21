/**
 * Asset Grid Column Configuration
 *
 * CENTRALIZED CONTROL PANEL
 * ==========================
 * This file is your single source of truth for the asset grid.
 *
 * TO CHANGE HEADER NAMES: Edit the 'headerName' property
 * TO CHANGE COLUMN WIDTH: Add 'width' property (default is auto-size)
 * TO CHANGE COLUMN ORDER: Rearrange items in the view presets at the bottom
 * TO ADD/REMOVE COLUMNS: Add to columnRegistry, then include in view presets
 */

import type { ColDef, ValueFormatterParams } from 'ag-grid-community'
import BadgeCell from '@/components/ui/BadgeCell.vue'
import {
  propertyTypeEnumMap,
  occupancyEnumMap,
  assetStatusEnumMap,
  activeTracksEnumMap,
  activeTasksColorMap,
  getAssetMasterStatusEnumMap
} from '@/GlobalStandardizations/badges'

// =============================================================================
// FORMATTERS - Reusable formatting functions
// =============================================================================

export const formatters = {
  currency: (params: ValueFormatterParams): string => {
    const v = params.value
    const num = typeof v === 'number' ? v : parseFloat(String(v))
    if (Number.isNaN(num)) return v == null ? '' : String(v)
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(num)
  },

  date: (params: ValueFormatterParams): string => {
    const v = params.value
    if (!v) return ''
    const d = new Date(String(v))
    if (isNaN(d.getTime())) return String(v)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(d)
  },

  percent: (params: ValueFormatterParams): string => {
    const v = params.value
    if (v == null || v === '') return ''
    const num = typeof v === 'number' ? v : parseFloat(String(v))
    if (Number.isNaN(num)) return String(v)
    return `${num.toFixed(2)}%`
  },

  moic: (params: ValueFormatterParams): string => {
    const v = params.value
    if (v == null || v === '') return ''
    const num = typeof v === 'number' ? v : parseFloat(String(v))
    if (Number.isNaN(num)) return String(v)
    return num.toFixed(2)
  },

  interestRate: (params: ValueFormatterParams): string => {
    const v = params.value
    if (v == null) return ''
    return `${(Number(v) * 100).toFixed(2)}%`
  },
}

// =============================================================================
// COLUMN REGISTRY
// =============================================================================
// Define ALL available columns here. Each column has a unique key.
// Change header names, widths, and formatting in this section.

export const columnRegistry: Record<string, ColDef> = {
  // -------------------------
  // CORE PROPERTY INFO
  // -------------------------
  servicer_id: {
    headerName: 'Servicer ID',           // 👈 CHANGE HEADER NAME HERE
    field: 'servicer_id',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueGetter: (p: any) => {
      const row = p.data ?? {}
      const explicitServicerId = row.servicer_id ?? row.servicerId
      if (explicitServicerId != null && explicitServicerId !== '') return explicitServicerId
      const hubServicerId = row.asset_hub?.servicer_id ?? row.asset_hub?.servicerId
      if (hubServicerId != null && hubServicerId !== '') return hubServicerId
      return ''
    },
  },
  trade_name: {
    headerName: 'Trade',                 // 👈 CHANGE HEADER NAME HERE
    field: 'trade_name',
    width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    cellClass: 'text-start',
  },

  street_address: {
    headerName: 'Property Address',      // 👈 CHANGE HEADER NAME HERE
    field: 'street_address',
    maxWidth: 260,                       // WHAT: Allow address a bit wider than default cap
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },

  city: {
    headerName: 'City',                  // 👈 CHANGE HEADER NAME HERE
    field: 'city',
    maxWidth: 160,                       // WHAT: Keep city compact without truncating
    headerClass: ['ag-left-aligned-header', 'text-start'],
    cellClass: ['ag-left-aligned-cell', 'text-start'],
  },

  state: {
    headerName: 'State',                 // 👈 CHANGE HEADER NAME HERE
    field: 'state',
    // width: 80,                         // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  // -------------------------
  // ASSET CLASSIFICATION
  // -------------------------
  property_type: {
    headerName: 'Property Type',         // 👈 CHANGE HEADER NAME HERE
    field: 'property_type',
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: propertyTypeEnumMap,
      size: 'xs2',                       // WHAT: In-between badge size for dense grid rows
    },
  },

  occupancy: {
    headerName: 'Occupancy',             // 👈 CHANGE HEADER NAME HERE
    field: 'occupancy',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: occupancyEnumMap,
    },
  },



  asset_class: {
    headerName: 'Asset Class',           // 👈 CHANGE HEADER NAME HERE
    field: 'asset_class',
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: assetStatusEnumMap,
      size: 'xs2',                       // WHAT: In-between badge size for dense grid rows
    },
  },

  asset_master_status: {
    headerName: 'Asset Master Status',   // 👈 CHANGE HEADER NAME HERE
    field: 'asset_master_status',
    // width: 180,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    editable: true,
    cellEditor: 'agSelectCellEditor',
    cellEditorParams: {
      values: ['ACTIVE', 'LIQUIDATED'],
    },
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'enum',
      enumMap: getAssetMasterStatusEnumMap(),
      size: 'xs2',                       // WHAT: In-between badge size for dense grid rows
    },
  },

  active_tracks: {
    headerName: 'Active Tracks',         // 👈 CHANGE HEADER NAME HERE
    field: 'active_tracks',
    width: 160,                          // 👈 FIXED WIDTH - badges wrap within this space
    wrapText: true,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'multi',
      enumMap: activeTracksEnumMap,
      size: 'xs2',                       // WHAT: Standardize to in-between badge size
    },
  },

  active_tasks: {
    headerName: 'Active Tasks',          // 👈 CHANGE HEADER NAME HERE
    field: 'active_tasks',
    width: 200,                          // 👈 FIXED WIDTH - task text wraps within this space
    wrapText: true,
    cellRenderer: BadgeCell as any,
    cellRendererParams: {
      mode: 'multi-prefix',
      colorMap: activeTasksColorMap,
      size: 'xs2',                       // WHAT: Standardize to in-between badge size
    },
  },

  lifecycle_status: {
    headerName: 'Lifecycle Status',      // 👈 CHANGE HEADER NAME HERE
    field: 'lifecycle_status',
    // width: 150,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  // -------------------------
  // VALUATION
  // -------------------------
  seller_asis_value: {
    headerName: 'Seller AIV',            // 👈 CHANGE HEADER NAME HERE
    field: 'seller_asis_value',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  seller_arv_value: {
    headerName: 'Seller ARV',            // 👈 CHANGE HEADER NAME HERE
    field: 'seller_arv_value',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  internal_initial_uw_asis_value: {
    headerName: 'Underwritten AIV',      // 👈 CHANGE HEADER NAME HERE
    field: 'internal_initial_uw_asis_value',
    // width: 150,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  internal_initial_uw_arv_value: {
    headerName: 'Underwritten ARV',      // 👈 CHANGE HEADER NAME HERE
    field: 'internal_initial_uw_arv_value',
    // width: 150,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  // -------------------------
  // PERFORMANCE METRICS
  // -------------------------
  acq_cost: {
    headerName: 'Acq Cost',              // 👈 CHANGE HEADER NAME HERE
    field: 'acq_cost',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  total_expenses: {
    headerName: 'Total Expenses',        // 👈 CHANGE HEADER NAME HERE
    field: 'total_expenses',
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  total_hold: {
    headerName: 'Total Hold (days)',     // 👈 CHANGE HEADER NAME HERE
    field: 'total_hold',
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  exit_date: {
    headerName: 'Exit Date',             // 👈 CHANGE HEADER NAME HERE
    field: 'exit_date',
    // width: 110,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  expected_gross_proceeds: {
    headerName: 'Gross Proceeds',        // 👈 CHANGE HEADER NAME HERE
    field: 'expected_gross_proceeds',
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  expected_net_proceeds: {
    headerName: 'Net Proceeds',          // 👈 CHANGE HEADER NAME HERE
    field: 'expected_net_proceeds',
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  expected_pl: {
    headerName: 'Expected P/L',          // 👈 CHANGE HEADER NAME HERE
    field: 'expected_pl',
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  expected_cf: {
    headerName: 'Expected CF',           // 👈 CHANGE HEADER NAME HERE
    field: 'expected_cf',
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  expected_irr: {
    headerName: 'IRR %',                 // 👈 CHANGE HEADER NAME HERE
    field: 'expected_irr',
    // width: 100,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.percent,
  },

  expected_moic: {
    headerName: 'MOIC',                  // 👈 CHANGE HEADER NAME HERE
    field: 'expected_moic',
    // width: 100,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.moic,
  },

  expected_npv: {
    headerName: 'NPV',                   // 👈 CHANGE HEADER NAME HERE
    field: 'expected_npv',
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  // -------------------------
  // SERVICING DATA
  // -------------------------
  s_as_of_date: {
    headerName: 'As Of',                 // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.as_of_date,
    // width: 110,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_current_balance: {
    headerName: 'Current Balance',       // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.current_balance,
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  s_total_debt: {
    headerName: 'Total Debt',            // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) =>
      p.data?.servicer_loan_data?.computed_total_debt
        ?? p.data?.servicer_loan_data?.total_debt,
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  s_interest_rate: {
    headerName: 'Interest Rate',         // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.interest_rate,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.interestRate,
  },

  s_next_due_date: {
    headerName: 'Next Due Date',         // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.next_due_date,
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_investor_id: {
    headerName: 'Investor ID',           // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.investor_id,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_servicer_id: {
    headerName: 'Servicer ID',           // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.servicer_id,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_fc_status: {
    headerName: 'FC Status',             // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.fc_status,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_bk_status: {
    headerName: 'BK Status',             // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.bk_current_status,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_loss_mit_status: {
    headerName: 'Loss Mit Status',       // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.loss_mitigation_status,
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_current_pi: {
    headerName: 'Current P&I',           // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.current_pi,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  s_current_ti: {
    headerName: 'Current T&I',           // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.current_ti,
    // width: 120,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  s_piti: {
    headerName: 'PITI',                  // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.piti,
    // width: 110,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.currency,
  },

  s_bk_filed_date: {
    headerName: 'BK Filed',              // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.bk_filed_date,
    // width: 110,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_bk_discharge_date: {
    headerName: 'BK Discharge',          // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.bk_discharge_date,
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_bk_dismissed_date: {
    headerName: 'BK Dismissed',          // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.bk_dismissed_date,
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_fc_scheduled_sale_date: {
    headerName: 'FC Scheduled Sale',     // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.scheduled_fc_sale_date,
    // width: 150,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_fc_actual_sale_date: {
    headerName: 'FC Actual Sale',        // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.actual_fc_sale_date,
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_fc_ba_status_date: {
    headerName: 'FC BA Status Date',     // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.foreclosure_business_area_status_date,
    // width: 160,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_fc_ba_status: {
    headerName: 'FC BA Status',          // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.foreclosure_business_area_status,
    // width: 130,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },

  s_loss_mit_start_date: {
    headerName: 'Loss Mit Start',        // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.loss_mitigation_start_date,
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_loan_mod_date: {
    headerName: 'Loan Mod Date',         // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.loan_modification_date,
    // width: 140,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
    valueFormatter: formatters.date,
  },

  s_repay_plan_status: {
    headerName: 'Repay Plan Status',     // 👈 CHANGE HEADER NAME HERE
    valueGetter: (p: any) => p.data?.servicer_loan_data?.repayment_plan_status,
    // width: 160,                        // 👈 UNCOMMENT TO SET FIXED WIDTH
  },
}

// =============================================================================
// VIEW PRESETS
// =============================================================================
// Define which columns appear in each view and their order.
// Drag and drop column keys to reorder, add/remove as needed.

export const viewPresets: Record<string, string[]> = {
  // -------------------------
  // SNAPSHOT VIEW
  // -------------------------
  // Quick overview of key asset details
  snapshot: [
    'asset_class',                       // 👈 DRAG TO REORDER
    'asset_master_status',               // 👈 DRAG TO REORDER
    'active_tracks',                     // 👈 DRAG TO REORDER
    'active_tasks',                      // 👈 DRAG TO REORDER
    'property_type',                     // 👈 DRAG TO REORDER
    'internal_initial_uw_asis_value',    // 👈 DRAG TO REORDER
    'internal_initial_uw_arv_value',     // 👈 DRAG TO REORDER
    's_current_balance',                 // 👈 DRAG TO REORDER
    's_total_debt',                      // 👈 DRAG TO REORDER
    's_interest_rate',                   // 👈 DRAG TO REORDER
    's_next_due_date',                   // 👈 DRAG TO REORDER
  ],

  // -------------------------
  // PERFORMANCE VIEW
  // -------------------------
  // Financial metrics and returns
  performance: [
    'acq_cost',                          // 👈 DRAG TO REORDER
    'total_expenses',                    // 👈 DRAG TO REORDER
    'expected_pl',                       // 👈 DRAG TO REORDER
    'expected_cf',                       // 👈 DRAG TO REORDER
    'expected_irr',                      // 👈 DRAG TO REORDER
    'expected_moic',                     // 👈 DRAG TO REORDER
    'expected_npv',                      // 👈 DRAG TO REORDER
  ],

  // -------------------------
  // VALUATION VIEW
  // -------------------------
  // Property valuations
  valuation: [
    'seller_asis_value',                 // 👈 DRAG TO REORDER
    'seller_arv_value',                  // 👈 DRAG TO REORDER
    'internal_initial_uw_asis_value',    // 👈 DRAG TO REORDER
    'internal_initial_uw_arv_value',     // 👈 DRAG TO REORDER
  ],

  // -------------------------
  // SERVICING VIEW
  // -------------------------
  // Detailed servicing data
  servicing: [
    's_as_of_date',                      // 👈 DRAG TO REORDER
    's_investor_id',                     // 👈 DRAG TO REORDER
    's_servicer_id',                     // 👈 DRAG TO REORDER
    's_current_balance',                 // 👈 DRAG TO REORDER
    's_interest_rate',                   // 👈 DRAG TO REORDER
    's_current_pi',                      // 👈 DRAG TO REORDER
    's_current_ti',                      // 👈 DRAG TO REORDER
    's_piti',                            // 👈 DRAG TO REORDER
    's_total_debt',                      // 👈 DRAG TO REORDER
    's_next_due_date',                   // 👈 DRAG TO REORDER
    's_fc_status',                       // 👈 DRAG TO REORDER
    's_bk_status',                       // 👈 DRAG TO REORDER
    's_loss_mit_status',                 // 👈 DRAG TO REORDER
    's_bk_filed_date',                   // 👈 DRAG TO REORDER
    's_bk_discharge_date',               // 👈 DRAG TO REORDER
    's_bk_dismissed_date',               // 👈 DRAG TO REORDER
    's_fc_scheduled_sale_date',          // 👈 DRAG TO REORDER
    's_fc_actual_sale_date',             // 👈 DRAG TO REORDER
    's_fc_ba_status_date',               // 👈 DRAG TO REORDER
    's_fc_ba_status',                    // 👈 DRAG TO REORDER
    's_loss_mit_start_date',             // 👈 DRAG TO REORDER
    's_loan_mod_date',                   // 👈 DRAG TO REORDER
    's_repay_plan_status',               // 👈 DRAG TO REORDER
  ],

  // -------------------------
  // ALL VIEW
  // -------------------------
  // Every available column
  all: Object.keys(columnRegistry),      // 👈 Automatically includes all columns
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get column definitions for a specific view
 */
export function getColumnsForView(viewName: string): ColDef[] {
  const columnKeys = viewPresets[viewName] || viewPresets.snapshot
  return columnKeys
    .map(key => columnRegistry[key])
    .filter(col => col !== undefined)
}

/**
 * Get constant columns (always pinned left)
 */
export function getConstantColumns(): string[] {
  return [ 'trade_name','servicer_id','street_address', 'city', 'state' ]  //Add pinned columns here
}

/**
 * Build full column definitions including constant columns
 */
export function buildColumnDefs(viewName: string, actionsColumn: ColDef): ColDef[] {
  const constantCols = getConstantColumns().map(key => columnRegistry[key])
  const viewCols = getColumnsForView(viewName)

  return [
    actionsColumn,  // Actions always first
    ...constantCols.map(col => ({ ...col, pinned: 'left' as const })),
    ...viewCols,
  ]
}

/**
 * Get list of columns with fixed widths (excluded from auto-sizing)
 */
export function getFixedWidthColumns(): string[] {
  return Object.entries(columnRegistry)
    .filter(([_, col]) => col.width !== undefined)
    .map(([key, _]) => key)
}
