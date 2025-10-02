<template>
  <!-- WHAT: Reusable P&L Metrics component with 3-column grid comparing Underwritten vs Realized -->
  <!-- WHY: Modular component for performance metrics that can be imported anywhere -->
  <!-- HOW: Clean grid layout with Purchase Cost, Acq Costs, Gross Cost, Expenses, Income, Proceeds -->
  <!-- WHERE: Used in PerformanceTab.vue (frontend_vue/src/views/am_module/loanlvl/tabs/PerformanceTab.vue) -->
  <div>
    <!-- Expand/Collapse All Button -->
    <div class="d-flex justify-content-end mb-2">
      <button 
        type="button"
        class="btn btn-sm btn-outline-secondary"
        @click="toggleAllSections"
      >
        <i :class="allExpanded ? 'mdi mdi-chevron-up' : 'mdi mdi-chevron-down'" class="me-1"></i>
        {{ allExpanded ? 'Collapse All' : 'Expand All' }}
      </button>
    </div>

    <!-- 4-Column Grid Layout: Headers | Underwritten | Realized | Sandbox -->
    <div class="table-responsive">
      <table class="table align-middle mb-0 performance-grid">
        <!-- Header Row -->
        <thead class="table-light">
          <tr>
            <th scope="col" class="metric-header">Performance Summary</th>
            <th scope="col" class="text-center underwritten-col">Underwritten</th>
            <th scope="col" class="text-center realized-col">Realized</th>
            <th scope="col" class="text-center sandbox-col">Sandbox</th>
          </tr>
        </thead>
        <tbody>
          <!-- Gross Cost (collapsible parent) -->
          <tr 
            @click="grossCostCollapsed = !grossCostCollapsed" 
            class="parent-row cursor-pointer"
          >
            <td class="fw-bold ps-3">
              <i :class="grossCostCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Gross Acquisition Cost
            </td>
            <td class="text-end fw-bold underwritten-col">{{ fmtCurrency(grossCost.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtCurrency(grossCost.realized) }}</td>
            <td class="text-end fw-bold sandbox-col">{{ fmtCurrency(grossCostSandbox) }}</td>
          </tr>

          <!-- Purchase Cost (sub-item) -->
          <tr v-show="!grossCostCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 3.65rem;">Purchase Cost</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.purchaseCost.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.purchaseCost.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Purchase Cost"
                v-model="sandboxDigits.purchaseCost"
              />
            </td>
          </tr>

          <!-- Acquisition Cost (collapsible sub-item) -->
          <tr 
            v-show="!grossCostCollapsed"
            @click="acqCostsCollapsed = !acqCostsCollapsed" 
            style="cursor: pointer;"
            role="button"
            :aria-expanded="!acqCostsCollapsed"
            title="Click to expand/collapse acquisition cost details"
          >
            <td class="ps-4 small fw-semibold text-muted">
              <i :class="acqCostsCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Acquisition Cost
            </td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(acqCostsTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(acqCostsTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtCurrency(acqCostsSandboxTotal) }}</td>
          </tr>

          <!-- Acquisition Cost Sub-items (nested) -->
          <tr v-show="!grossCostCollapsed && !acqCostsCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Due Diligence</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.acqDueDiligence.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.acqDueDiligence.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Due Diligence"
                v-model="sandboxDigits.acqDueDiligence"
              />
            </td>
          </tr>
          <tr v-show="!grossCostCollapsed && !acqCostsCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Legal</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.acqLegal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.acqLegal.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Legal"
                v-model="sandboxDigits.acqLegal"
              />
            </td>
          </tr>
          <tr v-show="!grossCostCollapsed && !acqCostsCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Title</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.acqTitle.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.acqTitle.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Title"
                v-model="sandboxDigits.acqTitle"
              />
            </td>
          </tr>
          <tr v-show="!grossCostCollapsed && !acqCostsCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Other</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.acqOther.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.acqOther.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Other"
                v-model="sandboxDigits.acqOther"
              />
            </td>
          </tr>

          <!-- Income (Total) - Collapsible -->
          <tr 
            @click="incomeCollapsed = !incomeCollapsed" 
            class="parent-row cursor-pointer"
            role="button"
            :aria-expanded="!incomeCollapsed"
            title="Click to expand/collapse income details"
          >
            <td class="fw-semibold ps-3">
              <i :class="incomeCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Income
            </td>
            <td class="text-end underwritten-col">{{ fmtCurrency(incomeTotal.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(incomeTotal.realized) }}</td>
            <td class="text-end sandbox-col">{{ fmtCurrency(incomeSandboxTotal) }}</td>
          </tr>

          <!-- Income Sub-lines (collapsible) -->
          <tr v-show="!incomeCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 3.65rem;">Principal Collected</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.incomePrincipal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.incomePrincipal.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Principal Collected"
                v-model="sandboxDigits.incomePrincipal"
              />
            </td>
          </tr>
          <tr v-show="!incomeCollapsed">
            <td class="small text-muted" style="padding-left: 3.65rem;">Interest Collected</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.incomeInterest.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.incomeInterest.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Interest Collected"
                v-model="sandboxDigits.incomeInterest"
              />
            </td>
          </tr>
          <tr v-show="!incomeCollapsed">
            <td class="small text-muted" style="padding-left: 3.65rem;">Rent Collected</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.incomeRent.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.incomeRent.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Rent Collected"
                v-model="sandboxDigits.incomeRent"
              />
            </td>
          </tr>
          <tr v-show="!incomeCollapsed">
            <td class="small text-muted" style="padding-left: 3.65rem;">CAM Income</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.incomeCAM.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.incomeCAM.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox CAM Income"
                v-model="sandboxDigits.incomeCAM"
              />
            </td>
          </tr>
          <tr v-show="!incomeCollapsed">
            <td class="small text-muted" style="padding-left: 3.65rem;">Mod Down Payment</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.incomeModDownPayment.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.incomeModDownPayment.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Mod Down Payment"
                v-model="sandboxDigits.incomeModDownPayment"
              />
            </td>
          </tr>

          <!-- Expenses (Parent Toggle) - Collapsible -->
          <tr 
            @click="allExpensesCollapsed = !allExpensesCollapsed" 
            class="parent-row cursor-pointer"
            role="button"
            :aria-expanded="!allExpensesCollapsed"
            title="Click to expand/collapse all expense categories"
          >
            <td class="fw-bold ps-3">
              <i :class="allExpensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Expenses
            </td>
            <td class="text-end fw-bold underwritten-col">{{ fmtExpense(operatingExpensesTotal.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtExpense(operatingExpensesTotal.realized) }}</td>
            <td class="text-end fw-bold sandbox-col">{{ fmtExpense(expensesSandboxTotal + reoExpensesSandboxTotal + fundExpensesSandboxTotal) }}</td>
          </tr>

          <!-- Operating Expense (nested under Expenses) - Collapsible -->
          <tr 
            v-show="!allExpensesCollapsed"
            @click="expensesCollapsed = !expensesCollapsed" 
            class="cursor-pointer"
            role="button"
            :aria-expanded="!expensesCollapsed"
            title="Click to expand/collapse operating expense details"
          >
            <td class="fw-semibold ps-4 small text-muted">
              <i :class="expensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Operating Expense
            </td>
            <td class="text-end underwritten-col small">{{ fmtExpense(operatingExpensesTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(operatingExpensesTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtExpense(expensesSandboxTotal) }}</td>
          </tr>

          <!-- Operating Expense Sub-lines (collapsible) -->
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Servicing Fees</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.expenseServicing.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.expenseServicing.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Servicing Fees"
                v-model="sandboxDigits.expenseServicing"
              />
            </td>
          </tr>
          <!-- Legal/DIL Cost (collapsible sub-item) -->
          <tr 
            v-show="!allExpensesCollapsed && !expensesCollapsed"
            @click="legalCostsCollapsed = !legalCostsCollapsed" 
            style="cursor: pointer;"
            role="button"
            :aria-expanded="!legalCostsCollapsed"
            title="Click to expand/collapse legal cost details"
          >
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small fw-semibold text-muted" style="padding-left: 4.3rem; font-size: 0.7rem;">
              <i :class="legalCostsCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Legal/DIL Cost
            </td>
            <td class="text-end underwritten-col small">{{ fmtExpense(legalTotals.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(legalTotals.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtExpense(legalCostsSandboxTotal) }}</td>
          </tr>

          <!-- Legal/DIL Cost Sub-items (nested) -->
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed && !legalCostsCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Foreclosure Fees</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.legalForeclosure.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.legalForeclosure.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Foreclosure Fees"
                v-model="sandboxDigits.legalForeclosure"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed && !legalCostsCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Bankruptcy Fees</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.legalBankruptcy.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.legalBankruptcy.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Bankruptcy Fees"
                v-model="sandboxDigits.legalBankruptcy"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed && !legalCostsCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Deed-in-Lieu Cost</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.legalDIL.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.legalDIL.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Deed-in-Lieu Cost"
                v-model="sandboxDigits.legalDIL"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed && !legalCostsCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Cash for Keys Cost</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.legalCashForKeys.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.legalCashForKeys.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Cash for Keys Cost"
                v-model="sandboxDigits.legalCashForKeys"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed && !legalCostsCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Eviction Cost</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.legalEviction.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.legalEviction.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Eviction Cost"
                v-model="sandboxDigits.legalEviction"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">AM Fees</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.expenseAMFees.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.expenseAMFees.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox AM Fees"
                v-model="sandboxDigits.expenseAMFees"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Property Taxes</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.expensePropertyTax.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.expensePropertyTax.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Property Taxes"
                v-model="sandboxDigits.expensePropertyTax"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !expensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Property Insurance</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.expensePropertyInsurance.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.expensePropertyInsurance.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Property Insurance"
                v-model="sandboxDigits.expensePropertyInsurance"
              />
            </td>
          </tr>

          <!-- REO Expenses (nested under Expenses) - Collapsible -->
          <tr 
            v-show="!allExpensesCollapsed"
            @click="reoExpensesCollapsed = !reoExpensesCollapsed" 
            class="cursor-pointer"
            role="button"
            :aria-expanded="!reoExpensesCollapsed"
            title="Click to expand/collapse REO expense details"
          >
            <td class="fw-semibold ps-4 small text-muted">
              <i :class="reoExpensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              REO Expenses
            </td>
            <td class="text-end underwritten-col small">{{ fmtExpense(reoExpensesTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(reoExpensesTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtExpense(reoExpensesSandboxTotal) }}</td>
          </tr>

          <!-- REO Expense Sub-lines (collapsible) -->
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">HOA</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoHOA.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoHOA.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox HOA"
                v-model="sandboxDigits.reoHOA"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Utilities</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoUtilities.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoUtilities.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Utilities"
                v-model="sandboxDigits.reoUtilities"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Trashout Cost</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoTrashout.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoTrashout.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Trashout Cost"
                v-model="sandboxDigits.reoTrashout"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Renovation Cost</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoRenovation.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoRenovation.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Renovation Cost"
                v-model="sandboxDigits.reoRenovation"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Property Preservation</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoPropertyPreservation.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoPropertyPreservation.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Property Preservation"
                v-model="sandboxDigits.reoPropertyPreservation"
              />
            </td>
          </tr>

          <!-- CRE Expenses (Total) - Collapsible -->
          <tr 
            v-show="!allExpensesCollapsed && !reoExpensesCollapsed"
            @click="creExpensesCollapsed = !creExpensesCollapsed" 
            style="cursor: pointer;"
            role="button"
            :aria-expanded="!creExpensesCollapsed"
            title="Click to expand/collapse CRE expense details"
          >
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small fw-semibold text-muted" style="padding-left: 4.2rem; font-size: 0.65rem;">
              <i :class="creExpensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              CRE Expenses
            </td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(creExpensesTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(creExpensesTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtCurrency(creExpensesSandboxTotal) }}</td>
          </tr>

          <!-- CRE Expense Sub-lines (collapsible) -->
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed && !creExpensesCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Marketing</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.creMarketing.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.creMarketing.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Marketing"
                v-model="sandboxDigits.creMarketing"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed && !creExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">G&A Pool/Groundskeeping</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.creGAPool.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.creGAPool.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox G&A Pool/Groundskeeping"
                v-model="sandboxDigits.creGAPool"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !reoExpensesCollapsed && !creExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 6.5rem; font-size: 0.65rem;">Maintenance</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.creMaintenance.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.creMaintenance.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Maintenance"
                v-model="sandboxDigits.creMaintenance"
              />
            </td>
          </tr>

          <!-- Fund Expenses (nested under Expenses) - Collapsible -->
          <tr 
            v-show="!allExpensesCollapsed"
            @click="fundExpensesCollapsed = !fundExpensesCollapsed" 
            class="cursor-pointer"
            role="button"
            :aria-expanded="!fundExpensesCollapsed"
            title="Click to expand/collapse fund expense details"
          >
            <td class="fw-semibold ps-4 small text-muted">
              <i :class="fundExpensesCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Fund Expenses
            </td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(fundExpensesTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(fundExpensesTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtCurrency(fundExpensesSandboxTotal) }}</td>
          </tr>

          <!-- Fund Expense Sub-lines (collapsible) -->
          <tr v-show="!allExpensesCollapsed && !fundExpensesCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Taxes</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.fundTaxes.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.fundTaxes.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Fund Taxes"
                v-model="sandboxDigits.fundTaxes"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !fundExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Legal</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.fundLegal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.fundLegal.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Fund Legal"
                v-model="sandboxDigits.fundLegal"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !fundExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Consulting</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.fundConsulting.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.fundConsulting.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Fund Consulting"
                v-model="sandboxDigits.fundConsulting"
              />
            </td>
          </tr>
          <tr v-show="!allExpensesCollapsed && !fundExpensesCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Audit</td>
            <td class="text-end underwritten-col small">{{ fmtCurrency(metrics.fundAudit.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtCurrency(metrics.fundAudit.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Fund Audit"
                v-model="sandboxDigits.fundAudit"
              />
            </td>
          </tr>

          <!-- Gross Liquidation Proceeds -->
          <tr>
            <td class="fw-semibold ps-3">Gross Liquidation Proceeds</td>
            <td class="text-end underwritten-col">{{ fmtCurrency(metrics.proceeds.underwritten) }}</td>
            <td class="text-end realized-col">{{ fmtCurrency(metrics.proceeds.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Gross Liquidation Proceeds"
                v-model="sandboxDigits.proceeds"
              />
            </td>
          </tr>

          <!-- Closing Costs (collapsible sub-item) -->
          <tr 
            @click="closingCostsCollapsed = !closingCostsCollapsed" 
            style="cursor: pointer;"
            role="button"
            :aria-expanded="!closingCostsCollapsed"
            title="Click to expand/collapse closing costs details"
          >
            <td class="ps-4 small fw-semibold text-muted">
              <i :class="closingCostsCollapsed ? 'mdi mdi-chevron-right' : 'mdi mdi-chevron-down'" class="me-1"></i>
              Closing Costs
            </td>
            <td class="text-end underwritten-col small">{{ fmtExpense(closingCostsTotal.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(closingCostsTotal.realized) }}</td>
            <td class="text-end sandbox-col small">{{ fmtExpense(closingCostsSandboxTotal) }}</td>
          </tr>

          <!-- Closing Costs Sub-items (nested) -->
          <tr v-show="!closingCostsCollapsed">
            <!-- TODO: Replace manual padding with CSS class system for consistent alignment -->
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Broker Closing Costs</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoBrokerClosing.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoBrokerClosing.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Broker Closing Costs"
                v-model="sandboxDigits.reoBrokerClosing"
              />
            </td>
          </tr>
          <tr v-show="!closingCostsCollapsed">
            <td class="small text-muted" style="padding-left: 5.5rem; font-size: 0.7rem;">Other Closing Costs</td>
            <td class="text-end underwritten-col small">{{ fmtExpense(metrics.reoOtherClosing.underwritten) }}</td>
            <td class="text-end realized-col small">{{ fmtExpense(metrics.reoOtherClosing.realized) }}</td>
            <td class="text-end sandbox-col">
              <input
                v-currency
                class="form-control form-control-sm text-end"
                inputmode="numeric"
                pattern="[0-9,]*"
                aria-label="Sandbox Other Closing Costs"
                v-model="sandboxDigits.reoOtherClosing"
              />
            </td>
          </tr>

          <!-- Net Liquidation Proceeds (calculated) -->
          <tr>
            <td class="fw-bold ps-3">Net Liquidation Proceeds</td>
            <td class="text-end fw-bold underwritten-col">{{ fmtCurrency(netLiquidationProceeds.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtCurrency(netLiquidationProceeds.realized) }}</td>
            <td class="text-end fw-bold sandbox-col">{{ fmtCurrency(netLiquidationProceedsSandbox) }}</td>
          </tr>

          <!-- Net P&L (calculated) - BOTTOM LINE -->
          <tr class="table-success bottom-line-row">
            <td class="fw-bold ps-3">Net P&L</td>
            <td class="text-end fw-bold underwritten-col">{{ fmtCurrency(netPL.underwritten) }}</td>
            <td class="text-end fw-bold realized-col">{{ fmtCurrency(netPL.realized) }}</td>
            <td class="text-end fw-bold sandbox-col">{{ fmtCurrency(netPLSandbox) }}</td>
          </tr>

          <!-- MOIC / Annualized ROI (Combined) -->
          <tr>
            <td class="fw-semibold ps-3">MOIC / Annualized ROI</td>
            <td class="text-end underwritten-col">{{ moic.underwritten }}x / {{ aroi.underwritten }}%</td>
            <td class="text-end realized-col">{{ moic.realized }}x / {{ aroi.realized }}%</td>
            <td class="text-end sandbox-col">{{ moicSandbox }}x / {{ aroiSandbox }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
// WHAT: Reusable P&L metrics component with Underwritten vs Realized comparison
// WHY: Modular component for easy reuse across different views
// HOW: Fetches data from backend API (/api/am/performance-summary/<asset_hub_id>/)
// WHERE: Used in PerformanceTab.vue (frontend_vue/src/views/am_module/loanlvl/tabs/PerformanceTab.vue)
import { withDefaults, defineProps, reactive, computed, ref, onMounted, watch } from 'vue'
import http from '@/lib/http'

// WHAT: Props interface for component
// WHY: Accept row data from parent to load metrics
// HOW: Optional row and assetHubId props
const props = withDefaults(defineProps<{ 
  row?: Record<string, any> | null
  assetHubId?: string | number | null 
}>(), {
  row: null,
  assetHubId: null,
})

// WHAT: Loading state for API call
// WHY: Show loading indicator while fetching data
const loading = ref(false)

// WHAT: Error state for API call
// WHY: Display error message if fetch fails
const error = ref<string | null>(null)

// WHAT: Main metrics object with underwritten vs realized values
// WHY: Separate columns for comparison; each metric has two values
// HOW: Replace with API data from backend (AcqModel for underwritten, TBD for realized)
const metrics = reactive({
  // Purchase Cost (actual purchase price)
  purchaseCost: {
    underwritten: 0,
    realized: 0,
  },
  // Acquisition Cost sub-items
  acqDueDiligence: {
    underwritten: 0,
    realized: 0,
  },
  acqLegal: {
    underwritten: 0,
    realized: 0,
  },
  acqTitle: {
    underwritten: 0,
    realized: 0,
  },
  acqOther: {
    underwritten: 0,
    realized: 0,
  },
  // Expenses (total - computed from sub-items)
  expenses: {
    underwritten: 0,
    realized: 0,
  },
  // Expense sub-items
  expenseServicing: {
    underwritten: 0,
    realized: 0,
  },
  // Legal/DIL Cost sub-items
  legalForeclosure: {
    underwritten: 0,
    realized: 0,
  },
  legalBankruptcy: {
    underwritten: 0,
    realized: 0,
  },
  legalDIL: {
    underwritten: 0,
    realized: 0,
  },
  legalCashForKeys: {
    underwritten: 0,
    realized: 0,
  },
  legalEviction: {
    underwritten: 0,
    realized: 0,
  },
  expenseAMFees: {
    underwritten: 0,
    realized: 0,
  },
  expensePropertyTax: {
    underwritten: 0,
    realized: 0,
  },
  expensePropertyInsurance: {
    underwritten: 0,
    realized: 0,
  },
  // REO Expenses (total - computed from sub-items)
  reoExpenses: {
    underwritten: 0,
    realized: 0,
  },
  // REO Expense sub-items
  reoHOA: {
    underwritten: 0,
    realized: 0,
  },
  reoUtilities: {
    underwritten: 0,
    realized: 0,
  },
  reoTrashout: {
    underwritten: 0,
    realized: 0,
  },
  reoRenovation: {
    underwritten: 0,
    realized: 0,
  },
  reoBrokerClosing: {
    underwritten: 0,
    realized: 0,
  },
  reoOtherClosing: {
    underwritten: 0,
    realized: 0,
  },
  reoPropertyPreservation: {
    underwritten: 0,
    realized: 0,
  },
  // CRE Expenses (total - computed from sub-items)
  creExpenses: {
    underwritten: 0,
    realized: 0,
  },
  // CRE Expense sub-items
  creMarketing: {
    underwritten: 0,
    realized: 0,
  },
  creGAPool: {
    underwritten: 0,
    realized: 0,
  },
  creMaintenance: {
    underwritten: 0,
    realized: 0,
  },
  // Fund Expenses (total - computed from sub-items)
  fundExpenses: {
    underwritten: 0,
    realized: 0,
  },
  // Fund Expense sub-items
  fundTaxes: {
    underwritten: 0,
    realized: 0,
  },
  fundLegal: {
    underwritten: 0,
    realized: 0,
  },
  fundConsulting: {
    underwritten: 0,
    realized: 0,
  },
  fundAudit: {
    underwritten: 0,
    realized: 0,
  },
  // Income (total - computed from sub-items)
  income: {
    underwritten: 0,
    realized: 0,
  },
  // Income sub-items
  incomePrincipal: {
    underwritten: 0,
    realized: 0,
  },
  incomeInterest: {
    underwritten: 0,
    realized: 0,
  },
  incomeRent: {
    underwritten: 0,
    realized: 0,
  },
  incomeCAM: {
    underwritten: 0,
    realized: 0,
  },
  incomeModDownPayment: {
    underwritten: 0,
    realized: 0,
  },
  // Proceeds (sale proceeds)
  proceeds: {
    underwritten: 0,
    realized: 0,
  },
})

// WHAT: Collapse state for Income sub-items
// WHY: Allow users to toggle visibility of income breakdown
// HOW: Boolean reactive ref, toggled by clicking Income row
// NOTE: Defaults to true (collapsed) for cleaner initial view
const incomeCollapsed = ref(true)

// WHAT: Collapse state for overall Expenses section
// WHY: Allow users to toggle visibility of all expense categories
// HOW: Boolean reactive ref, toggled by clicking Expenses parent row
// NOTE: Defaults to true (collapsed) for cleaner initial view
const allExpensesCollapsed = ref(true)

// WHAT: Collapse state for Operating Expense sub-items
// WHY: Allow users to toggle visibility of operating expense breakdown (nested under Expenses)
// HOW: Boolean reactive ref, toggled by clicking Operating Expense row
const expensesCollapsed = ref(false)

// WHAT: Collapse state for REO Expense sub-items
// WHY: Allow users to toggle visibility of REO expense breakdown
const reoExpensesCollapsed = ref(false)

// WHAT: Collapse state for Fund Expense sub-items
// WHY: Allow users to toggle visibility of fund expense breakdown
const fundExpensesCollapsed = ref(false)

// WHAT: Collapse state for Gross Cost
// WHY: Allow users to toggle visibility of Purchase Cost and Acquisition Cost breakdown
// NOTE: Defaults to true (collapsed) for cleaner initial view
const grossCostCollapsed = ref(true)

// WHAT: Collapse state for Acquisition Cost sub-items
// WHY: Allow users to toggle visibility of acq cost breakdown (nested under Gross Cost)
const acqCostsCollapsed = ref(false)

// WHAT: Collapse state for CRE Expense sub-items
// WHY: Allow users to toggle visibility of CRE expense breakdown (nested under REO)
const creExpensesCollapsed = ref(false)

// WHAT: Collapse state for Closing Costs
// WHY: Allow users to toggle visibility of closing costs breakdown (under Gross Liquidation Proceeds)
// NOTE: Defaults to true (collapsed) for cleaner initial view
const closingCostsCollapsed = ref(true)

// WHAT: Collapse state for Legal/DIL Costs
// WHY: Allow users to toggle visibility of legal cost breakdown (nested under Operating Expenses)
const legalCostsCollapsed = ref(false)

// WHAT: Track if all sections are expanded
// WHY: Control expand/collapse all button state
const allExpanded = computed(() => {
  return !grossCostCollapsed.value && 
         !acqCostsCollapsed.value && 
         !incomeCollapsed.value && 
         !allExpensesCollapsed.value &&
         !expensesCollapsed.value && 
         !legalCostsCollapsed.value && 
         !reoExpensesCollapsed.value && 
         !creExpensesCollapsed.value && 
         !fundExpensesCollapsed.value && 
         !closingCostsCollapsed.value
})

// WHAT: Toggle all collapsible sections at once
// WHY: Provide quick way to expand or collapse all details
// HOW: If any section is collapsed, expand all; if all expanded, collapse all
function toggleAllSections() {
  const shouldExpand = !allExpanded.value
  grossCostCollapsed.value = !shouldExpand
  acqCostsCollapsed.value = !shouldExpand
  incomeCollapsed.value = !shouldExpand
  allExpensesCollapsed.value = !shouldExpand
  expensesCollapsed.value = !shouldExpand
  legalCostsCollapsed.value = !shouldExpand
  reoExpensesCollapsed.value = !shouldExpand
  creExpensesCollapsed.value = !shouldExpand
  fundExpensesCollapsed.value = !shouldExpand
  closingCostsCollapsed.value = !shouldExpand
}

// WHAT: Sandbox digits-only model (strings) for editable inputs using v-currency
// WHY: Follow platform directive policy to store numeric digits as string
// HOW: Initialize from underwritten values by default for quick what-if tweaks
const sandboxDigits = reactive({
  purchaseCost: '0',
  // Acquisition Cost sub-items (digits-only strings)
  acqDueDiligence: '0',
  acqLegal: '0',
  acqTitle: '0',
  acqOther: '0',
  // Income sub-items (digits-only strings)
  incomePrincipal: '0',
  incomeInterest: '0',
  incomeRent: '0',
  incomeCAM: '0',
  incomeModDownPayment: '0',
  // Expense sub-items (digits-only strings)
  expenseServicing: '0',
  // Legal/DIL Cost sub-items (digits-only strings)
  legalForeclosure: '0',
  legalBankruptcy: '0',
  legalDIL: '0',
  legalCashForKeys: '0',
  legalEviction: '0',
  expenseAMFees: '0',
  expensePropertyTax: '0',
  expensePropertyInsurance: '0',
  // REO Expense sub-items (digits-only strings)
  reoHOA: '0',
  reoUtilities: '0',
  reoTrashout: '0',
  reoRenovation: '0',
  reoBrokerClosing: '0',
  reoOtherClosing: '0',
  reoPropertyPreservation: '0',
  // CRE Expense sub-items (digits-only strings)
  creMarketing: '0',
  creGAPool: '0',
  creMaintenance: '0',
  // Fund Expense sub-items (digits-only strings)
  fundTaxes: '0',
  fundLegal: '0',
  fundConsulting: '0',
  fundAudit: '0',
  proceeds: '0',
})

// WHAT: Initialize sandbox with best available data
// WHY: Prioritize realized (actual) over underwritten (projected) for more accurate scenarios
// HOW: Use realized if available, fallback to underwritten, then 0
function initSandboxFromBestAvailable() {
  // Helper: Pick realized first, then underwritten, then 0
  // Convert to integer to avoid decimal issues, then to string for v-currency
  const pickBest = (metric: any) => String(Math.round(metric.realized || metric.underwritten || 0))
  
  sandboxDigits.purchaseCost = pickBest(metrics.purchaseCost)
  sandboxDigits.acqDueDiligence = pickBest(metrics.acqDueDiligence)
  sandboxDigits.acqLegal = pickBest(metrics.acqLegal)
  sandboxDigits.acqTitle = pickBest(metrics.acqTitle)
  sandboxDigits.acqOther = pickBest(metrics.acqOther)
  sandboxDigits.incomePrincipal = pickBest(metrics.incomePrincipal)
  sandboxDigits.incomeInterest = pickBest(metrics.incomeInterest)
  sandboxDigits.incomeRent = pickBest(metrics.incomeRent)
  sandboxDigits.incomeCAM = pickBest(metrics.incomeCAM)
  sandboxDigits.incomeModDownPayment = pickBest(metrics.incomeModDownPayment)
  sandboxDigits.expenseServicing = pickBest(metrics.expenseServicing)
  sandboxDigits.legalForeclosure = pickBest(metrics.legalForeclosure)
  sandboxDigits.legalBankruptcy = pickBest(metrics.legalBankruptcy)
  sandboxDigits.legalDIL = pickBest(metrics.legalDIL)
  sandboxDigits.legalCashForKeys = pickBest(metrics.legalCashForKeys)
  sandboxDigits.legalEviction = pickBest(metrics.legalEviction)
  sandboxDigits.expenseAMFees = pickBest(metrics.expenseAMFees)
  sandboxDigits.expensePropertyTax = pickBest(metrics.expensePropertyTax)
  sandboxDigits.expensePropertyInsurance = pickBest(metrics.expensePropertyInsurance)
  sandboxDigits.reoHOA = pickBest(metrics.reoHOA)
  sandboxDigits.reoUtilities = pickBest(metrics.reoUtilities)
  sandboxDigits.reoTrashout = pickBest(metrics.reoTrashout)
  sandboxDigits.reoRenovation = pickBest(metrics.reoRenovation)
  sandboxDigits.reoBrokerClosing = pickBest(metrics.reoBrokerClosing)
  sandboxDigits.reoOtherClosing = pickBest(metrics.reoOtherClosing)
  sandboxDigits.reoPropertyPreservation = pickBest(metrics.reoPropertyPreservation)
  sandboxDigits.creMarketing = pickBest(metrics.creMarketing)
  sandboxDigits.creGAPool = pickBest(metrics.creGAPool)
  sandboxDigits.creMaintenance = pickBest(metrics.creMaintenance)
  sandboxDigits.fundTaxes = pickBest(metrics.fundTaxes)
  sandboxDigits.fundLegal = pickBest(metrics.fundLegal)
  sandboxDigits.fundConsulting = pickBest(metrics.fundConsulting)
  sandboxDigits.fundAudit = pickBest(metrics.fundAudit)
  sandboxDigits.proceeds = pickBest(metrics.proceeds)
}
initSandboxFromBestAvailable()

// WHAT: Convert digits-only strings to numbers safely
// WHY: Inputs store digits per v-currency; computations need numbers
const toNumber = (s: string | number | null | undefined): number => {
  if (s == null) return 0
  const str = String(s)
  const digits = str.replace(/[^0-9]/g, '')
  return Number(digits || 0)
}

// WHAT: Acquisition Cost total from backend (BACKEND-COMPUTED)
// WHY: Single source of truth - backend sums all acq cost sub-items
const acqCostsTotal = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox acquisition cost total (sum of sub-items)
const acqCostsSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.acqDueDiligence) + 
         toNumber(sandboxDigits.acqLegal) + 
         toNumber(sandboxDigits.acqTitle) + 
         toNumber(sandboxDigits.acqOther)
})

// WHAT: Gross Cost from backend (BACKEND-COMPUTED)
// WHY: Single source of truth - backend computes Purchase Cost + Acquisition Costs
const grossCost = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox gross cost computed from editable inputs
const grossCostSandbox = computed(() => {
  return toNumber(sandboxDigits.purchaseCost) + acqCostsSandboxTotal.value
})

// WHAT: Sandbox income total (sum of sub-items)
// WHY: Income is now broken into Principal, Interest, Rent
const incomeSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.incomePrincipal) + 
         toNumber(sandboxDigits.incomeInterest) + 
         toNumber(sandboxDigits.incomeRent) + 
         toNumber(sandboxDigits.incomeCAM) + 
         toNumber(sandboxDigits.incomeModDownPayment)
})

// WHAT: Legal/DIL Cost total (BACKEND-COMPUTED)
// WHY: Single source of truth from backend rollup
const legalTotals = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox Legal/DIL cost total (sum of sub-items)
const legalCostsSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.legalForeclosure) + 
         toNumber(sandboxDigits.legalBankruptcy) + 
         toNumber(sandboxDigits.legalDIL) + 
         toNumber(sandboxDigits.legalCashForKeys) + 
         toNumber(sandboxDigits.legalEviction)
})

// WHAT: Rollup totals from API (backend computed)
// WHY: Single source of truth - backend calculates all parent row totals
// HOW: Populated from API response fields: *_total_underwritten, *_total_realized
const incomeTotal = reactive({
  underwritten: 0,
  realized: 0,
})

const reoExpensesTotal = reactive({
  underwritten: 0,
  realized: 0,
})

const creExpensesTotal = reactive({
  underwritten: 0,
  realized: 0,
})

const fundExpensesTotal = reactive({
  underwritten: 0,
  realized: 0,
})

const operatingExpensesTotal = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox expense total (sum of sub-items)
// WHY: Expenses broken into Servicing, Legal/DIL (total), AM Fees, Property Tax, Property Insurance
const expensesSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.expenseServicing) + 
         legalCostsSandboxTotal.value + 
         toNumber(sandboxDigits.expenseAMFees) + 
         toNumber(sandboxDigits.expensePropertyTax) + 
         toNumber(sandboxDigits.expensePropertyInsurance) + 
         reoExpensesSandboxTotal.value + 
         fundExpensesSandboxTotal.value
})

// WHAT: Sandbox CRE expense total (sum of sub-items)
// WHY: CRE expenses broken into Marketing, G&A Pool/Groundskeeping, Maintenance
const creExpensesSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.creMarketing) + 
         toNumber(sandboxDigits.creGAPool) + 
         toNumber(sandboxDigits.creMaintenance)
})

// WHAT: Sandbox REO expense total (sum of sub-items)
// WHY: REO expenses broken into HOA, Utilities, Trashout, Renovation, Property Preservation, + CRE total
// NOTE: Broker/Other Closing moved to Liquidation Proceeds section
const reoExpensesSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.reoHOA) + 
         toNumber(sandboxDigits.reoUtilities) + 
         toNumber(sandboxDigits.reoTrashout) + 
         toNumber(sandboxDigits.reoRenovation) + 
         toNumber(sandboxDigits.reoPropertyPreservation) + 
         creExpensesSandboxTotal.value
})

// WHAT: Closing Costs total from backend (BACKEND-COMPUTED)
// WHY: Single source of truth - backend sums Broker + Other closing costs
const closingCostsTotal = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox Closing Costs total
const closingCostsSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.reoBrokerClosing) + toNumber(sandboxDigits.reoOtherClosing)
})

// WHAT: Net Liquidation Proceeds from backend (BACKEND-COMPUTED)
// WHY: Single source of truth - backend stores expected_net_proceeds
const netLiquidationProceeds = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox Net Liquidation Proceeds
const netLiquidationProceedsSandbox = computed(() => {
  return toNumber(sandboxDigits.proceeds) - closingCostsSandboxTotal.value
})

// WHAT: Sandbox fund expense total (sum of sub-items)
// WHY: Fund expenses broken into Taxes, Legal, Consulting, Audit
const fundExpensesSandboxTotal = computed(() => {
  return toNumber(sandboxDigits.fundTaxes) + 
         toNumber(sandboxDigits.fundLegal) + 
         toNumber(sandboxDigits.fundConsulting) + 
         toNumber(sandboxDigits.fundAudit)
})

// WHAT: Net P&L from backend (BACKEND-COMPUTED)
// WHY: Single source of truth for bottom-line calculation
// HOW: Backend computes: (Proceeds + Income) - (Operating Expenses + Gross Cost)
const netPL = reactive({
  underwritten: 0,
  realized: 0,
})

// WHAT: Sandbox Net P&L computed from editable inputs
// NOTE: Income and all Expense categories now use computed totals from sub-items
const netPLSandbox = computed(() => {
  const income = incomeSandboxTotal.value
  const proceeds = toNumber(sandboxDigits.proceeds)
  const expenses = expensesSandboxTotal.value + reoExpensesSandboxTotal.value + fundExpensesSandboxTotal.value
  return (income + proceeds) - (grossCostSandbox.value + expenses)
})

// WHAT: Variance = Realized Net P&L - Underwritten Net P&L
// WHY: Shows how much better/worse we did vs projection
// HOW: Subtract underwritten from realized Net P&L
const variance = computed(() => netPL.realized - netPL.underwritten)

// WHAT: Dynamic CSS class for variance (green if positive, red if negative)
// WHY: Visual indicator of performance vs underwriting
// HOW: Return Bootstrap text color classes based on variance sign
const varianceClass = computed(() => {
  if (variance.value > 0) return 'text-success'
  if (variance.value < 0) return 'text-danger'
  return ''
})

// WHAT: Variance vs Underwritten for Sandbox
const varianceSandbox = computed(() => netPLSandbox.value - netPL.underwritten)
const varianceSandboxClass = computed(() => {
  if (varianceSandbox.value > 0) return 'text-success'
  if (varianceSandbox.value < 0) return 'text-danger'
  return ''
})

// WHAT: ROI calculations (Net P&L / Gross Cost * 100)
// WHY: Standard return on investment metric in percentage
// HOW: Divide Net P&L by Gross Cost, multiply by 100, format to 1 decimal
const roiUnderwritten = computed(() => {
  if (grossCost.underwritten === 0) return 0
  return ((netPL.underwritten / grossCost.underwritten) * 100).toFixed(1)
})

const roiRealized = computed(() => {
  if (grossCost.realized === 0) return 0
  return ((netPL.realized / grossCost.realized) * 100).toFixed(1)
})

// WHAT: ROI for Sandbox
const roiSandbox = computed(() => {
  if (grossCostSandbox.value === 0) return 0
  return ((netPLSandbox.value / grossCostSandbox.value) * 100).toFixed(1)
})
const roiSandboxClass = computed(() => {
  const n = Number(roiSandbox.value)
  if (n > Number(roiUnderwritten.value)) return 'text-success'
  if (n < Number(roiUnderwritten.value)) return 'text-danger'
  return ''
})

// WHAT: MOIC (Multiple on Invested Capital) = Total Return / Gross Cost
// WHY: Shows how many times the investment was multiplied
// HOW: (Net P&L + Gross Cost) / Gross Cost = Total Proceeds / Gross Cost
const moic = computed(() => ({
  underwritten: grossCost.underwritten === 0 ? 0 : 
    ((netPL.underwritten + grossCost.underwritten) / grossCost.underwritten).toFixed(2),
  realized: grossCost.realized === 0 ? 0 : 
    ((netPL.realized + grossCost.realized) / grossCost.realized).toFixed(2),
}))

// WHAT: MOIC for Sandbox
const moicSandbox = computed(() => {
  if (grossCostSandbox.value === 0) return '0.00'
  return ((netPLSandbox.value + grossCostSandbox.value) / grossCostSandbox.value).toFixed(2)
})

// WHAT: AROI (Annualized Return on Investment)
// WHY: Shows annualized return percentage (assumes 1 year holding period for now)
// HOW: ROI / holding period in years (currently hardcoded to 1 year)
// TODO: Add holding period input field for accurate AROI calculation
const aroi = computed(() => ({
  underwritten: roiUnderwritten.value,
  realized: roiRealized.value,
}))

// WHAT: AROI for Sandbox
const aroiSandbox = computed(() => {
  return roiSandbox.value
})

// WHAT: Variance as percentage relative to underwritten
// WHY: Relative variance is more meaningful than absolute dollar amount
// HOW: Divide variance by absolute underwritten Net P&L, multiply by 100
const variancePercent = computed(() => {
  if (netPL.underwritten === 0) return 0
  return ((variance.value / Math.abs(netPL.underwritten)) * 100).toFixed(1)
})

// WHAT: Currency formatter helper function
// WHY: Consistent USD formatting across all currency fields
// HOW: Uses Intl.NumberFormat with no decimals, shows negative numbers in parentheses
function fmtCurrency(v: number | null | undefined): string {
  const n = Number(v || 0)
  if (n === 0) return '—'
  
  const abs = Math.abs(n)
  const formatted = new Intl.NumberFormat('en-US', { 
    minimumFractionDigits: 0,
    maximumFractionDigits: 0 
  }).format(abs)
  
  // WHAT: Show negative numbers in parentheses (accounting format)
  return n < 0 ? `($${formatted})` : `$${formatted}`
}

// WHAT: Format expenses as negative (in parentheses)
// WHY: Expenses reduce profit, so they should display as negative in accounting format
function fmtExpense(v: number | null | undefined): string {
  const n = Number(v || 0)
  if (n === 0) return '—'
  
  // Negate the value to show as expense
  return fmtCurrency(-Math.abs(n))
}

// ------------------------------
// API Data Fetching
// ------------------------------
// WHAT: Fetch performance summary data from backend
// WHY: Load underwritten/realized values from BlendedOutcomeModel
// HOW: Call /api/am/performance-summary/<asset_hub_id>/ and populate metrics
async function fetchPerformanceData() {
  if (!props.assetHubId) {
    console.warn('PLMetrics: No assetHubId provided, using placeholder data')
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await http.get(`/am/performance-summary/${props.assetHubId}/`)
    const data = response.data

    // WHAT: Map API response to metrics object
    // WHY: API uses snake_case, frontend uses camelCase
    // HOW: Destructure and assign each field
    
    // Gross Cost section
    metrics.purchaseCost.underwritten = data.purchase_cost_underwritten || 0
    metrics.purchaseCost.realized = data.purchase_cost_realized || 0
    
    metrics.acqDueDiligence.underwritten = data.acq_due_diligence_underwritten || 0
    metrics.acqDueDiligence.realized = data.acq_due_diligence_realized || 0
    
    metrics.acqLegal.underwritten = data.acq_legal_underwritten || 0
    metrics.acqLegal.realized = data.acq_legal_realized || 0
    
    metrics.acqTitle.underwritten = data.acq_title_underwritten || 0
    metrics.acqTitle.realized = data.acq_title_realized || 0
    
    metrics.acqOther.underwritten = data.acq_other_underwritten || 0
    metrics.acqOther.realized = data.acq_other_realized || 0
    
    // Income section
    metrics.incomePrincipal.underwritten = data.income_principal_underwritten || 0
    metrics.incomePrincipal.realized = data.income_principal_realized || 0
    
    metrics.incomeInterest.underwritten = data.income_interest_underwritten || 0
    metrics.incomeInterest.realized = data.income_interest_realized || 0
    
    metrics.incomeRent.underwritten = data.income_rent_underwritten || 0
    metrics.incomeRent.realized = data.income_rent_realized || 0
    
    metrics.incomeCAM.underwritten = data.income_cam_underwritten || 0
    metrics.incomeCAM.realized = data.income_cam_realized || 0
    
    metrics.incomeModDownPayment.underwritten = data.income_mod_down_payment_underwritten || 0
    metrics.incomeModDownPayment.realized = data.income_mod_down_payment_realized || 0
    
    // Operating Expenses section
    metrics.expenseServicing.underwritten = data.expense_servicing_underwritten || 0
    metrics.expenseServicing.realized = data.expense_servicing_realized || 0
    
    // Legal/DIL Cost sub-items
    metrics.legalForeclosure.underwritten = data.legal_foreclosure_underwritten || 0
    metrics.legalForeclosure.realized = data.legal_foreclosure_realized || 0
    
    metrics.legalBankruptcy.underwritten = data.legal_bankruptcy_underwritten || 0
    metrics.legalBankruptcy.realized = data.legal_bankruptcy_realized || 0
    
    metrics.legalDIL.underwritten = data.legal_dil_underwritten || 0
    metrics.legalDIL.realized = data.legal_dil_realized || 0
    
    metrics.legalCashForKeys.underwritten = data.legal_cash_for_keys_underwritten || 0
    metrics.legalCashForKeys.realized = data.legal_cash_for_keys_realized || 0
    
    metrics.legalEviction.underwritten = data.legal_eviction_underwritten || 0
    metrics.legalEviction.realized = data.legal_eviction_realized || 0
    
    metrics.expenseAMFees.underwritten = data.expense_am_fees_underwritten || 0
    metrics.expenseAMFees.realized = data.expense_am_fees_realized || 0
    
    metrics.expensePropertyTax.underwritten = data.expense_property_tax_underwritten || 0
    metrics.expensePropertyTax.realized = data.expense_property_tax_realized || 0
    
    metrics.expensePropertyInsurance.underwritten = data.expense_property_insurance_underwritten || 0
    metrics.expensePropertyInsurance.realized = data.expense_property_insurance_realized || 0
    
    // REO Expenses section
    metrics.reoHOA.underwritten = data.reo_hoa_underwritten || 0
    metrics.reoHOA.realized = data.reo_hoa_realized || 0
    
    metrics.reoUtilities.underwritten = data.reo_utilities_underwritten || 0
    metrics.reoUtilities.realized = data.reo_utilities_realized || 0
    
    metrics.reoTrashout.underwritten = data.reo_trashout_underwritten || 0
    metrics.reoTrashout.realized = data.reo_trashout_realized || 0
    
    metrics.reoRenovation.underwritten = data.reo_renovation_underwritten || 0
    metrics.reoRenovation.realized = data.reo_renovation_realized || 0
    
    metrics.reoPropertyPreservation.underwritten = data.reo_property_preservation_underwritten || 0
    metrics.reoPropertyPreservation.realized = data.reo_property_preservation_realized || 0
    
    // CRE Expenses
    metrics.creMarketing.underwritten = data.cre_marketing_underwritten || 0
    metrics.creMarketing.realized = data.cre_marketing_realized || 0
    
    metrics.creGAPool.underwritten = data.cre_ga_pool_underwritten || 0
    metrics.creGAPool.realized = data.cre_ga_pool_realized || 0
    
    metrics.creMaintenance.underwritten = data.cre_maintenance_underwritten || 0
    metrics.creMaintenance.realized = data.cre_maintenance_realized || 0
    
    // Fund Expenses section
    metrics.fundTaxes.underwritten = data.fund_taxes_underwritten || 0
    metrics.fundTaxes.realized = data.fund_taxes_realized || 0
    
    metrics.fundLegal.underwritten = data.fund_legal_underwritten || 0
    metrics.fundLegal.realized = data.fund_legal_realized || 0
    
    metrics.fundConsulting.underwritten = data.fund_consulting_underwritten || 0
    metrics.fundConsulting.realized = data.fund_consulting_realized || 0
    
    metrics.fundAudit.underwritten = data.fund_audit_underwritten || 0
    metrics.fundAudit.realized = data.fund_audit_realized || 0
    
    // Proceeds section
    metrics.proceeds.underwritten = data.proceeds_underwritten || 0
    metrics.proceeds.realized = data.proceeds_realized || 0
    
    metrics.reoBrokerClosing.underwritten = data.broker_closing_underwritten || 0
    metrics.reoBrokerClosing.realized = data.broker_closing_realized || 0
    
    metrics.reoOtherClosing.underwritten = data.other_closing_underwritten || 0
    metrics.reoOtherClosing.realized = data.other_closing_realized || 0
    
    // WHAT: Populate Net Liquidation Proceeds from backend
    // WHY: Backend stores expected_net_proceeds field
    netLiquidationProceeds.underwritten = data.net_liquidation_proceeds_underwritten || 0
    netLiquidationProceeds.realized = data.net_liquidation_proceeds_realized || 0
    
    // WHAT: Populate Gross Cost from backend
    // WHY: Backend computes Purchase Cost + Acquisition Costs
    grossCost.underwritten = data.gross_cost_total_underwritten || 0
    grossCost.realized = data.gross_cost_total_realized || 0
    
    // WHAT: Populate Acquisition Costs Total from backend
    acqCostsTotal.underwritten = data.acq_costs_total_underwritten || 0
    acqCostsTotal.realized = data.acq_costs_total_realized || 0
    
    // WHAT: Populate Closing Costs Total from backend
    closingCostsTotal.underwritten = data.closing_costs_total_underwritten || 0
    closingCostsTotal.realized = data.closing_costs_total_realized || 0
    
    // WHAT: Populate rollup totals from backend API
    // WHY: Backend computes all parent row sums for consistency
    incomeTotal.underwritten = data.income_total_underwritten || 0
    incomeTotal.realized = data.income_total_realized || 0
    
    legalTotals.underwritten = data.legal_costs_total_underwritten || 0
    legalTotals.realized = data.legal_costs_total_realized || 0
    
    operatingExpensesTotal.underwritten = data.operating_expenses_total_underwritten || 0
    operatingExpensesTotal.realized = data.operating_expenses_total_realized || 0
    
    reoExpensesTotal.underwritten = data.reo_expenses_total_underwritten || 0
    reoExpensesTotal.realized = data.reo_expenses_total_realized || 0
    
    creExpensesTotal.underwritten = data.cre_expenses_total_underwritten || 0
    creExpensesTotal.realized = data.cre_expenses_total_realized || 0
    
    fundExpensesTotal.underwritten = data.fund_expenses_total_underwritten || 0
    fundExpensesTotal.realized = data.fund_expenses_total_realized || 0
    
    // WHAT: Populate Net P&L from backend
    // WHY: Backend computes bottom-line profitability
    netPL.underwritten = data.net_pl_underwritten || 0
    netPL.realized = data.net_pl_realized || 0
    
    // Re-initialize sandbox from newly loaded data (prioritizes realized over underwritten)
    initSandboxFromBestAvailable()
    
    console.log('PLMetrics: Data loaded successfully', data)
  } catch (err: any) {
    console.error('PLMetrics: Failed to fetch performance data', err)
    error.value = err.response?.data?.detail || 'Failed to load performance data'
  } finally {
    loading.value = false
  }
}

// WHAT: Fetch data on component mount
// WHY: Load data when component first renders
onMounted(() => {
  fetchPerformanceData()
})

// WHAT: Watch assetHubId changes
// WHY: Refetch data if user switches to different asset
watch(() => props.assetHubId, () => {
  fetchPerformanceData()
})
</script>

<style scoped>
/* WHAT: Custom styles for 4-column performance grid */
/* WHY: Make the grid easy to scan with clear visual hierarchy */
/* HOW: Column colors, spacing, subtle underlines, and hover effects per Hyper UI patterns */

/* Table cell padding */
.performance-grid > :not(caption) > * > * { 
  padding: .625rem 1rem; 
}

/* Remove default borders, add subtle bottom border to each row */
.performance-grid tbody tr:not(.spacer-row) td {
  border-bottom: 1px solid #e9ecef;
}

/* WHAT: Subtle fill for parent toggle rows */
/* WHY: Visually distinguish collapsible sections from their children */
/* HOW: Target rows with parent-row class (all collapsible section headers) */
.performance-grid tbody tr.parent-row {
  background-color: #f8f9fa;
}

/* Dashed borders for sub-line items (indented rows) */
.performance-grid tbody tr td.ps-5,
.performance-grid tbody tr td[style*="padding-left"] {
  border-bottom: 1px dashed #e9ecef !important;
}

/* Parent row of dashed items also gets dashed */
.performance-grid tbody tr:has(+ tr td.ps-5) td,
.performance-grid tbody tr:has(+ tr td[style*="padding-left"]) td {
  border-bottom: 1px dashed #e9ecef;
}

/* Header row styling */
.performance-grid thead th {
  border-bottom: 2px solid #dee2e6;
}

/* WHAT: Bottom line row styling (Net P&L) */
/* WHY: Emphasize the final profitability metric */
/* HOW: Double border top to separate from other rows */
.performance-grid tbody tr.bottom-line-row td {
  border-top: 3px double #198754 !important;
  border-bottom: 3px double #198754 !important;
  font-size: 1.05rem;
}

/* Metric header column styling */
.metric-header {
  min-width: 180px;
  font-weight: 600;
}

/* 
  WHAT: Underwritten column styling - subtle blue tint
  WHY: Visual distinction between Underwritten, Realized, and Sandbox columns
  NOTE: This color (#f0f7ff) is also used in cashFlowSeries.vue for Period/Date headers
  WHERE: cashFlowSeries.vue lines 39, 45, 59, 65 (inline styles)
  TO CHANGE: Update this background-color AND CashFlowSeries.vue inline styles
*/
.underwritten-col {
  background-color: #f0f7ff;
  width: 350px;
  min-width: 350px;
  max-width: 350px;
  font-weight: 500;
}

/* Realized column styling - subtle green tint */
.realized-col {
  background-color: #f0fdf4;
  width: 350px;
  min-width: 350px;
  max-width: 350px;
  font-weight: 500;
}

/* Sandbox column styling - subtle yellow tint */
.sandbox-col {
  background-color: #fffbeb;
  width: 350px;
  min-width: 350px;
  max-width: 350px;
  font-weight: 500;
}

/* Spacer rows for visual separation */
.spacer-row {
  height: 8px;
  background: transparent;
}

.spacer-row td {
  border: none !important;
  padding: 4px !important;
}

/* Hover effect for data rows */
.performance-grid tbody tr:not(.spacer-row):hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Calculated totals get extra emphasis and thicker border */
.table-secondary td,
.table-success td,
.table-info td {
  font-size: 0.95rem;
  border-bottom: 2px solid #dee2e6 !important;
}
</style>
