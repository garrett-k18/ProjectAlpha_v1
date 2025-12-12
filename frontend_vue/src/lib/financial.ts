/**
 * Financial calculation utilities for frontend
 * 
 * WHAT: Provides IRR, NPV, and other financial calculations for instant frontend updates
 * WHY: Enable real-time financial metric calculations without waiting for backend
 * WHERE: frontend_vue/src/lib/financial.ts
 * HOW: Uses node-irr library for XIRR calculations (with dates), standard NPV formula
 */

import { xirr } from 'node-irr'

/**
 * Calculate Internal Rate of Return (XIRR) from a cash flow series with dates.
 * 
 * WHAT: Calculates the annualized discount rate that makes NPV = 0 using actual dates
 * WHY: XIRR shows the annualized return rate accounting for actual cash flow timing (more accurate than IRR)
 * HOW: Uses node-irr's xirr() function which accepts cash flows with dates
 * 
 * NOTE: This is equivalent to Excel's XIRR function, which uses actual dates for more accurate calculations.
 * 
 * @param cashflows - Array of objects with amount and date
 *                    Format: [{ amount: -1000, date: '2025-01-15' }, { amount: 500, date: '2025-02-15' }, ...]
 *                    Date format: YYYY-MM-DD, YYYYMMDD, or YYYY/MM/DD
 * @returns Annualized IRR as decimal (e.g., 0.15 for 15% annual return), or 0.0 if calculation fails
 */
export function calculateXIRR(cashflows: Array<{ amount: number; date: string | Date }>): number {
  // WHAT: Validate input
  if (!cashflows || cashflows.length < 2) {
    return 0.0
  }
  
  // WHAT: Check if we have both positive and negative cash flows
  // WHY: IRR requires both investment (negative) and return (positive)
  const hasNegative = cashflows.some(cf => cf.amount < 0)
  const hasPositive = cashflows.some(cf => cf.amount > 0)
  
  if (!hasNegative || !hasPositive) {
    return 0.0
  }
  
  try {
    // WHAT: Calculate XIRR using node-irr library
    // WHY: xirr() returns annualized rate directly (no conversion needed)
    const result = xirr(cashflows)
    
    // WHAT: Extract rate from result (xirr returns { days: number, rate: number })
    const annualizedIRR = result.rate
    
    // WHAT: Validate result
    if (annualizedIRR == null || isNaN(annualizedIRR) || !isFinite(annualizedIRR)) {
      return 0.0
    }
    
    // WHAT: Cap annualized IRR at reasonable bounds (-99% to 1000%)
    if (annualizedIRR < -0.99 || annualizedIRR > 10.0) {
      return 0.0
    }
    
    return annualizedIRR
  } catch (error) {
    console.error('[calculateXIRR] Error calculating XIRR:', error)
    return 0.0
  }
}

/**
 * Calculate Net Present Value (NPV) from a cash flow series with dates.
 * 
 * WHAT: Calculates present value of future cash flows at a given discount rate using actual dates
 * WHY: NPV shows the value of investment in today's dollars, accounting for time value of money
 * HOW: Uses standard NPV formula with actual date-based discounting (more accurate than equal periods)
 * 
 * @param cashflows - Array of objects with amount and date
 *                    Format: [{ amount: -1000, date: '2025-01-15' }, { amount: 500, date: '2025-02-15' }, ...]
 *                    Date format: YYYY-MM-DD, YYYYMMDD, or YYYY/MM/DD, or Date object
 * @param discountRateAnnual - Annual discount rate as decimal (default 0.10 = 10%)
 * @returns NPV value in dollars, or 0.0 if calculation fails
 */
export function calculateNPV(cashflows: Array<{ amount: number; date: string | Date }>, discountRateAnnual: number = 0.10): number {
  if (!cashflows || cashflows.length === 0) {
    return 0.0
  }
  
  try {
    // WHAT: Parse first date as reference point
    const firstDate = typeof cashflows[0].date === 'string' 
      ? new Date(cashflows[0].date.replace(/-/g, '/')) 
      : cashflows[0].date
    
    if (isNaN(firstDate.getTime())) {
      return 0.0
    }
    
    // WHAT: Calculate NPV using actual dates
    let npv = 0
    for (const cf of cashflows) {
      const date = typeof cf.date === 'string' 
        ? new Date(cf.date.replace(/-/g, '/')) 
        : cf.date
      
      if (isNaN(date.getTime())) {
        continue
      }
      
      // WHAT: Calculate days from first date
      const daysDiff = (date.getTime() - firstDate.getTime()) / (1000 * 60 * 60 * 24)
      const yearsDiff = daysDiff / 365.25
      
      // WHAT: Discount factor based on actual time elapsed
      const discountFactor = Math.pow(1 + discountRateAnnual, yearsDiff)
      npv += cf.amount / discountFactor
    }
    
    // WHAT: Validate result
    if (isNaN(npv) || !isFinite(npv)) {
      return 0.0
    }
    
    return npv
  } catch (error) {
    console.error('[calculateNPV] Error calculating NPV:', error)
    return 0.0
  }
}
