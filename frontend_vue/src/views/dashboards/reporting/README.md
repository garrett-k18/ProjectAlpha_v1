# Reporting Dashboard

## Overview

Split-screen analytics dashboard with asymmetric layout (25% sidebar / 75% main content) optimized for power users who need deep analytical capabilities with progressive information disclosure.

**Route:** `/reporting`

**Features:**
- Persistent filter sidebar with primary dimensions (Trade, Status, Fund, Entity)
- Large chart area with interactive visualizations
- Progressive disclosure: Summary → Report Views → Deep Dives
- Click-through drill-downs from any chart
- Export capabilities for CSV/Excel/PDF
- Saved report configurations

---

## File Structure

```
frontend_vue/src/views/dashboards/reporting/
├── index_reporting.vue          # Main dashboard (split-screen layout)
├── README.md                     # This file
│
├── components/
│   ├── ReportingSidebar.vue     # Left panel: Filters + Navigation (25%)
│   ├── ReportHeader.vue         # Top KPI metrics bar
│   └── DrillDownModal.vue       # Deep dive modal overlay
│
├── views/                        # Report views (dynamically loaded)
│   ├── ByTradeReport.vue        # 🔥 PRIMARY: Performance by Trade
│   ├── ByStatusReport.vue       # 🔥 PRIMARY: Portfolio by Status
│   ├── ByFundReport.vue         # 🔥 PRIMARY: Performance by Fund
│   ├── ByEntityReport.vue       # 🔥 PRIMARY: Performance by Entity
│   ├── OverviewReport.vue       # Dashboard summary (default)
│   ├── GeographicReport.vue     # State/regional distribution
│   ├── CollateralReport.vue     # Property type/occupancy analysis
│   └── TimeSeriesReport.vue     # Trend analysis over time
│
└── drilldowns/                   # Detail views (modal overlays)
    ├── TradeDetails.vue         # Individual trade deep dive
    ├── StatusDetails.vue        # Status cohort analysis
    └── AssetDetails.vue         # Asset-level breakdown
```

---

## Data Store

**Location:** `frontend_vue/src/stores/reporting.ts`

### Primary Filters (Front & Center)
- **Trade** (`selectedTradeIds`) - Single or multi-select by trade
- **Status** (`selectedStatuses`) - Multi-select (DD, AWARDED, PASS, BOARD)
- **Fund** (`selectedFundId`) - Single fund selection
- **Entity** (`selectedEntityId`) - Single legal entity selection

### Secondary Filters
- **Date Range** (`dateRangeStart`, `dateRangeEnd`) - ISO date strings
- **Current View** (`currentView`) - Active report type

### Data State
- `reportSummary` - Top-level KPIs (Total UPB, Asset Count, Avg LTV, Delinquency Rate)
- `chartData` - Chart visualization data (format varies by view)
- `gridData` - Detailed table rows
- `savedReports` - User-saved report configurations

### Actions
```typescript
// Load dropdown options
fetchTradeOptions(force?: boolean)
fetchStatusOptions(force?: boolean)
fetchFundOptions(force?: boolean)
fetchEntityOptions(force?: boolean)

// Load report data
fetchReportSummary()  // Top bar KPIs
fetchChartData()      // Main visualizations
fetchGridData()       // Detail tables

// Mutations
resetFilters()        // Clear all filters
setView(viewName)     // Switch report view
refreshAllOptions()   // Force reload dropdowns
```

---

## Primary Report Views

### 1. By Trade Report (`ByTradeReport.vue`)
**Purpose:** Analyze performance across all trades

**Visualizations:**
- Bar/Line/Pie chart of UPB by trade
- Interactive chart with click-to-drill-down
- Sortable table with trade metrics

**Metrics:**
- Asset Count per trade
- Total UPB per trade
- Average LTV per trade
- Status badge

**Drill-Down:** Click any bar/row → Trade detail modal

---

### 2. By Status Report (`ByStatusReport.vue`)
**Purpose:** Portfolio breakdown by deal status

**Visualizations:**
- Doughnut chart showing status distribution
- Progress bars with UPB amounts
- Status breakdown summary panel

**Metrics:**
- Count per status
- Total UPB per status
- Percentage of total portfolio
- Average UPB per status

**Drill-Down:** Click any status → Status cohort analysis

---

### 3. By Fund Report (`ByFundReport.vue`)
**Purpose:** Compare performance across investment funds

**Visualizations:**
- Bar chart of UPB by fund
- Side panel with fund comparison cards

**Metrics:**
- Assets per fund
- Total UPB per fund
- Average LTV per fund
- Fund metadata (code, type)

**Drill-Down:** Click any fund → Fund detail view

---

### 4. By Entity Report (`ByEntityReport.vue`)
**Purpose:** Report by legal entity (for accounting/compliance)

**Visualizations:**
- Horizontal bar chart (entity as Y-axis)
- Entity type badges (LLC, LP, Corp)

**Metrics:**
- Assets per entity
- Total UPB per entity
- Average LTV per entity
- Entity type

**Drill-Down:** Click any entity → Entity breakdown

---

## Analytical Views

### Overview Report (`OverviewReport.vue`)
Default landing view with high-level portfolio summary, trend line, and recent activity feed.

### Geographic Report (`GeographicReport.vue`)
State-level distribution with map placeholder (integrate jVectorMap or similar) and top states table.

### Collateral Report (`CollateralReport.vue`)
Property type distribution (SFR, Condo, etc.) and occupancy status breakdown.

### Time Series Report (`TimeSeriesReport.vue`)
Dual-axis line chart showing UPB and asset count trends over time (quarterly).

---

## Drill-Down Modals

### Trade Details (`TradeDetails.vue`)
- Trade metadata (seller, status, bid date)
- Key metrics (UPB, LTV, debt, as-is value)
- State count, delinquency rate
- Actions: View full report, view assets

### Status Details (`StatusDetails.vue`)
- Status badge and portfolio percentage
- Count, Total UPB, Average UPB
- Breakdown table (avg LTV, total debt, delinquency)

### Asset Details (`AssetDetails.vue`)
- Asset ID, address, property type
- Current balance, LTV, state
- Link to full loan-level view

---

## Usage Examples

### 1. Filter by Trade and Status
```typescript
// User selects a trade and multiple statuses in sidebar
reportingStore.selectedTradeIds = [15]
reportingStore.selectedStatuses = ['DD', 'AWARDED']

// Apply filters triggers data refresh
await reportingStore.fetchReportSummary()
await reportingStore.fetchChartData()
await reportingStore.fetchGridData()
```

### 2. Switch Views
```typescript
// User clicks "By Status" in sidebar
reportingStore.setView('by-status')
// Dashboard automatically loads ByStatusReport.vue
```

### 3. Drill Down
```typescript
// User clicks a bar in the chart
function handleChartClick(data: any) {
  emit('drill-down', { type: 'trade', data })
}
// Parent opens DrillDownModal with TradeDetails.vue
```

---

## Backend Integration (TODO)

The frontend is ready and uses placeholder data. Wire these endpoints:

### Filter Options
- `GET /api/reporting/trades/` → `TradeOption[]`
- `GET /api/reporting/statuses/` → `StatusOption[]`
- `GET /api/reporting/funds/` → `FundOption[]`
- `GET /api/reporting/entities/` → `EntityOption[]`

### Report Data
- `GET /api/reporting/summary/?{filters}` → `ReportSummary`
- `GET /api/reporting/{viewName}/?{filters}` → `ChartDataPoint[]`
- `GET /api/reporting/{viewName}/grid/?{filters}` → `any[]`

### Export
- `POST /api/reporting/export/` → File blob (CSV/Excel/PDF)

**Query Params Format:**
```
?trade_ids=1,2,3&statuses=DD,AWARDED&fund_id=5&entity_id=2&start_date=2024-01-01&end_date=2024-12-31
```

---

## Styling & UI Components

**Framework:** Hyper UI + Bootstrap 5

**Icons:** Material Design Icons (`mdi mdi-*`)

**Charts:** Chart.js (via `chart.js` npm package)

**Grid:** Bootstrap tables (AG Grid integration coming later)

**Color Palette:**
- Primary (Blue): Trade, Info, Default actions
- Success (Green): Awarded status, positive metrics
- Warning (Yellow): Fund, LTV 90-100%
- Info (Cyan): DD status, Entity
- Danger (Red): LTV >100%, delinquency
- Secondary (Gray): Pass status

---

## Navigation

**Sidebar Quick Links:**
```
PRIMARY VIEWS
├─ 📊 By Trade      (by-trade)
├─ 🏷️  By Status    (by-status)
├─ 💼 By Fund       (by-fund)
└─ 🏢 By Entity     (by-entity)

ANALYTICAL VIEWS
├─ 🌐 Overview      (overview)
├─ 🗺️  Geographic   (geographic)
├─ 🏠 Collateral    (collateral)
└─ 📈 Time Series   (timeseries)
```

---

## Future Enhancements

1. **Saved Reports** - Persist filter configurations with names
2. **Scheduled Reports** - Email reports on schedule
3. **Export Templates** - Custom export formats per report type
4. **Comparison Mode** - Side-by-side trade/fund comparison
5. **Advanced Filters** - Property type, state, LTV ranges
6. **Real-time Updates** - WebSocket for live data refresh
7. **Custom Dashboards** - Drag-and-drop widget builder
8. **PDF Generation** - Server-side report rendering

---

## Key Design Decisions

### Why Split-Screen?
- **Power users** spend hours in reporting - dedicated sidebar prevents constant navigation
- **Filter persistence** - sidebar stays visible while exploring different views
- **Progressive disclosure** - Start broad (summary) → drill into specifics (modals)

### Why Primary Filters?
- **Trade/Status/Fund/Entity** are the most common business groupings
- Front-and-center placement reduces clicks
- Multi-select status enables cohort analysis

### Why Dynamic Components?
```typescript
<component :is="currentReportComponent" />
```
- Lazy-load only the active report view
- Reduces initial bundle size
- Easy to add new report types without changing layout

### Why Pinia Store?
- **Centralized state** - All reports share same filters
- **Caching** - Avoid redundant API calls
- **Reactivity** - Auto-refresh when filters change

---

## Developer Notes

### Adding a New Report View

1. **Create component:** `views/MyNewReport.vue`
2. **Import in index:** `import MyNewReport from './views/MyNewReport.vue'`
3. **Register component:** Add to `components` object
4. **Map view name:** Add `'my-view': MyNewReport` to `currentReportComponent` computed
5. **Add to sidebar:** Update `ReportingSidebar.vue` with new link
6. **Backend endpoint:** Create `/api/reporting/my-view/` endpoint

### Adding a New Filter

1. **Store state:** Add `selectedMyFilter` ref
2. **Store options:** Add `myFilterOptions` ref with loading/error
3. **Store action:** Add `fetchMyFilterOptions()`
4. **Sidebar UI:** Add dropdown/checkboxes in `ReportingSidebar.vue`
5. **Query params:** Update `filterQueryParams` computed
6. **Backend:** Accept `my_filter` query param

---

## Testing Checklist

- [ ] All primary filters (Trade/Status/Fund/Entity) functional
- [ ] View switching works (8 views total)
- [ ] Chart click events trigger drill-down modal
- [ ] Export button displays message (implementation pending)
- [ ] Settings modal opens
- [ ] Loading states display correctly
- [ ] Empty states display correctly
- [ ] Responsive layout works on mobile/tablet
- [ ] KPI metrics update when filters change
- [ ] Saved reports section ready (data pending)

---

## Performance Considerations

1. **Lazy Loading** - Report views loaded on-demand
2. **Chart Cleanup** - Destroy Chart.js instances before re-render
3. **Debounced Filters** - Apply filters on button click, not on every keystroke
4. **Cached Options** - Dropdown data cached in store
5. **Pagination** - Grid data paginated (implement with AG Grid)

---

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation for sidebar links
- Focus management in modals
- Color not sole indicator (use icons + text)
- Screen reader friendly tables

---

## Contact & Support

For questions about the reporting dashboard:
- Review this README
- Check `stores/reporting.ts` for data flow
- Inspect component props in each view file
- Reference existing acquisitions dashboard patterns

**Built with:** Vue 3, TypeScript, Pinia, Chart.js, Bootstrap 5, Hyper UI
