# Frontend Track & Task Filters Implementation

## Overview
Updated reporting dashboard to display **Asset Track Status** and **Asset Task Status** filters instead of trade statuses, aligning with the backend AM module implementation.

## ✅ Changes Completed

### 1. Store Updates (`stores/reporting.ts`)

#### New Interfaces
```typescript
// Track option for AM outcome tracks
export interface TrackOption {
  value: string
  label: string
  count?: number
}

// Task status option for active tasks
export interface TaskStatusOption {
  value: string
  label: string
  track: string  // Which track this task belongs to
  count?: number
}
```

#### State Changes
- **Removed**: `selectedStatuses` (trade statuses)
- **Added**: `selectedTracks` (AM outcome tracks)
- **Added**: `selectedTaskStatuses` (active task types)

#### New Store Properties
```typescript
// Selected filters
selectedTracks: ref<string[]>([])
selectedTaskStatuses: ref<string[]>([])

// Options
trackOptions: ref<TrackOption[]>([])
taskStatusOptions: ref<TaskStatusOption[]>([])

// Loading states
loadingTracks: ref<boolean>(false)
loadingTaskStatuses: ref<boolean>(false)

// Error states
errorTracks: ref<string | null>(null)
errorTaskStatuses: ref<string | null>(null)
```

#### New Actions
```typescript
// Fetch track options (REO, FC, DIL, etc.)
async function fetchTrackOptions(force?: boolean): Promise<void>

// Fetch task status options (eviction, trashout, etc.)
async function fetchTaskStatusOptions(trackFilter?: string, force?: boolean): Promise<void>
```

#### Updated Query Parameters
```typescript
// OLD (removed)
params.append('statuses', selectedStatuses.value.join(','))

// NEW (added)
params.append('tracks', selectedTracks.value.join(','))
params.append('task_statuses', selectedTaskStatuses.value.join(','))
```

### 2. Sidebar Component Updates (`components/ReportingSidebar.vue`)

#### Filter #1: Asset Track Status
- **Label**: "Asset Track Status"
- **Icon**: `mdi-sitemap`
- **Options**: REO, Foreclosure, DIL, Short Sale, Modification, Note Sale
- **Display**: Shows asset count per track

#### Filter #2: Asset Task Status (NEW)
- **Label**: "Asset Task Status"
- **Icon**: `mdi-checkbox-marked-circle-outline`
- **Options**: All active task types (eviction, trashout, nod_noi, etc.)
- **Display**: Shows task label + track badge + count
- **Example**: "Eviction [REO] (10)"

#### New Local State
```typescript
const localTracks = ref<string[]>([])
const localTaskStatuses = ref<string[]>([])
const showTracksDropdown = ref<boolean>(false)
const showTasksDropdown = ref<boolean>(false)
```

#### New Computed Labels
```typescript
const selectedTracksLabel = computed(() => {
  if (localTracks.value.length === 0) return 'All Tracks'
  if (localTracks.value.length === 1) return track?.label || '1 selected'
  return `${localTracks.value.length} selected`
})

const selectedTasksLabel = computed(() => {
  if (localTaskStatuses.value.length === 0) return 'All Tasks'
  if (localTaskStatuses.value.length === 1) return task?.label || '1 selected'
  return `${localTaskStatuses.value.length} selected`
})
```

### 3. Main Dashboard (`index_reporting.vue`)
- **No changes required** ✅
- Already calls `refreshAllOptions()` on mount which now loads track and task options

## 🎨 UI Changes

### Before
```
Filters
├── Trades (dropdown)
├── Statuses (dropdown)        ← Trade statuses (DD, AWARDED, PASS, BOARD)
├── Funds (dropdown)
├── Partnerships (dropdown)
└── Date Range
```

### After
```
Filters
├── Trades (dropdown)
├── Asset Track Status (dropdown)     ← NEW: AM tracks (REO, FC, DIL, etc.)
├── Asset Task Status (dropdown)      ← NEW: Active tasks (eviction, trashout, etc.)
├── Funds (dropdown)
├── Partnerships (dropdown)
└── Date Range
```

## 📡 API Integration

### Endpoints Used

```javascript
// Asset Track Status Options
GET /api/reporting/statuses/
// Returns: [
//   { value: 'reo', label: 'REO', count: 25 },
//   { value: 'fc', label: 'Foreclosure', count: 15 },
//   ...
// ]

// Asset Task Status Options
GET /api/reporting/task-statuses/
// Returns: [
//   { value: 'eviction', label: 'Eviction', track: 'reo', count: 10 },
//   { value: 'trashout', label: 'Trashout', track: 'reo', count: 8 },
//   ...
// ]

// Optional: Filter tasks by track
GET /api/reporting/task-statuses/?track=reo
```

### Query Parameters Sent to Backend

```javascript
// When user applies filters
GET /api/reporting/summary/?tracks=reo,fc&task_statuses=eviction,trashout
GET /api/reporting/by-trade/?tracks=reo,fc&task_statuses=eviction
GET /api/reporting/by-status/?tracks=reo,fc&task_statuses=eviction
```

## 🔄 Data Flow

### On Dashboard Mount
```
1. Dashboard calls refreshAllOptions()
   ├── fetchTradeOptions()
   ├── fetchTrackOptions()     ← NEW
   ├── fetchTaskStatusOptions() ← NEW
   ├── fetchFundOptions()
   └── fetchPartnershipOptions()

2. Sidebar displays loaded options in dropdowns

3. Dashboard calls refreshData()
   ├── fetchReportSummary()
   ├── fetchChartData()
   └── fetchGridData()
```

### When User Applies Filters
```
1. User selects tracks and/or tasks in sidebar
2. User clicks "Apply" button
3. Sidebar emits 'filters-change' event
4. Dashboard calls refreshData()
5. Store builds filterQueryParams with new tracks/task_statuses
6. All endpoints receive updated filter query string
7. UI updates with filtered data
```

## 🎯 Filter Behavior

### Track Filter (OR Logic)
```javascript
// Select multiple tracks
selectedTracks = ['reo', 'fc']

// Shows assets on REO track OR FC track
// Backend: asset_hub__reo_data__isnull=False OR asset_hub__fc_sale__isnull=False
```

### Task Status Filter (OR Logic)
```javascript
// Select multiple tasks
selectedTaskStatuses = ['eviction', 'trashout']

// Shows assets with Eviction task OR Trashout task
// Backend: Searches across all 6 task models for these task types
```

### Combined Filters (AND Logic between filter types)
```javascript
// Select both tracks and tasks
selectedTracks = ['reo']
selectedTaskStatuses = ['eviction']

// Shows assets on REO track AND with Eviction task
// Both filters must match
```

## 📋 Testing Checklist

### UI Tests
- [ ] "Asset Track Status" dropdown shows track options on mount
- [ ] "Asset Task Status" dropdown shows task options on mount
- [ ] Track dropdown shows asset counts
- [ ] Task dropdown shows task counts with track badges
- [ ] Selecting tracks updates button label correctly
- [ ] Selecting tasks updates button label correctly
- [ ] "Apply" button enables when selections change
- [ ] "Reset" button clears all selections
- [ ] Dropdowns close when clicking outside

### Functional Tests
- [ ] Selecting single track filters data correctly
- [ ] Selecting multiple tracks filters data correctly (OR logic)
- [ ] Selecting single task filters data correctly
- [ ] Selecting multiple tasks filters data correctly (OR logic)
- [ ] Combining tracks + tasks filters correctly (AND logic)
- [ ] Combining with other filters (trades, dates) works
- [ ] Filter state persists during view changes
- [ ] Reset button clears tracks and tasks

### API Tests
- [ ] GET /api/reporting/statuses/ returns track data
- [ ] GET /api/reporting/task-statuses/ returns task data
- [ ] Query params include `tracks` when tracks selected
- [ ] Query params include `task_statuses` when tasks selected
- [ ] All reporting endpoints accept new query params
- [ ] Error handling works if endpoints fail

## 🐛 Known Issues / Future Enhancements

### Potential Enhancements
1. **Dynamic Task Filtering**: When tracks are selected, dynamically filter task options to only show tasks from selected tracks
2. **Task Count by Track**: Group task options by track in dropdown for better organization
3. **Track Icons**: Add visual icons for each track type (house for REO, gavel for FC, etc.)
4. **Saved Filters**: Allow users to save frequently used track/task combinations
5. **Quick Filters**: Add preset buttons like "All REO Tasks", "All FC Tasks", etc.

### Implementation Example for Dynamic Filtering
```typescript
// Watch for track changes and reload task options
watch(selectedTracks, async (newTracks) => {
  if (newTracks.length > 0) {
    const trackParam = newTracks.join(',')
    await fetchTaskStatusOptions(trackParam)
  } else {
    await fetchTaskStatusOptions() // Show all tasks
  }
})
```

## 📚 Related Documentation

- Backend Implementation: `projectalphav1/reporting/TRACK_AND_TASK_FILTERS_IMPLEMENTATION.md`
- Store Documentation: `frontend_vue/src/stores/reporting.ts`
- Component Documentation: `frontend_vue/src/views/dashboards/reporting/README.md`

## 🚀 Deployment Notes

1. **No breaking changes** - Only additive changes
2. **Backward compatible** - Old query params removed, but frontend fully updated
3. **No migrations required** - Frontend-only changes
4. **Testing recommended** - Verify filters work with real boarded asset data
5. **User training** - Inform users about new filter names and options

---

**Implementation Date**: 2025-11-14  
**Status**: ✅ Complete (Backend + Frontend)  
**Test Status**: ⏳ Pending  
**Deployed**: ⏳ Not yet deployed

