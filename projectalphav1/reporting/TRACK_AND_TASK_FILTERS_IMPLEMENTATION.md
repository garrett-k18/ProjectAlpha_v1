# Asset Management Track & Task Filters Implementation

## Overview
Changed reporting module filters from **Trade Statuses** to **Asset Management Outcome Tracks** and **Active Task Statuses** to align with the AM module workflow.

## Changes Summary

### 1. Filter Options Service (`serv_rep_filterOptions.py`)

#### Updated `get_status_options_data()` → Now Returns AM Tracks
- **Changed From**: Trade statuses (DD, AWARDED, PASS, BOARD)
- **Changed To**: AM outcome tracks (REO, FC, DIL, Short Sale, Modification, Note Sale)
- **Data Source**: AssetIdHub outcome relationships (1:1 models)
- **Returns**: List of track options with counts

#### Added `get_task_status_options_data(track=None)`
- **Purpose**: Get active task types for filter dropdown
- **Optional Filtering**: Can filter by specific track (e.g., `?track=reo`)
- **Data Source**: All task models (REOtask, FCTask, DILTask, ShortSaleTask, ModificationTask, NoteSaleTask)
- **Returns**: List of task options with track association and counts

### 2. Query Builder (`serv_rep_queryBuilder.py`)

#### Replaced `apply_status_filter()` with `apply_track_filter()`
- **Purpose**: Filter by AM outcome tracks instead of trade statuses
- **Parameters**: `tracks: Optional[List[str]]` - list of track values (reo, fc, dil, etc.)
- **Logic**: Uses Q objects to check for existence of outcome model relationships on AssetIdHub

#### Added `apply_task_status_filter()`
- **Purpose**: Filter by active task types across all task models
- **Parameters**: `task_statuses: Optional[List[str]]` - list of task type values (eviction, trashout, etc.)
- **Logic**: Uses Q objects to search across all 6 task model relationships

#### Updated `build_reporting_queryset()`
- **Changed Parameters**:
  - Removed: `statuses: Optional[List[str]]`
  - Added: `tracks: Optional[List[str]]`
  - Added: `task_statuses: Optional[List[str]]`
- **Filter Chain**: Now applies track and task filters instead of status filter

#### Updated `parse_filter_params()`
- **Changed Query Params**:
  - Removed: `statuses` (parse trade statuses)
  - Added: `tracks` (parse AM outcome tracks)
  - Added: `task_statuses` (parse task types)

### 3. Views (`view_rep_filters.py`)

#### Updated `status_options()` View
- **Changed Purpose**: Now returns AM outcome tracks instead of trade statuses
- **Endpoint**: `GET /api/reporting/statuses/`
- **Returns**: List of track options (REO, FC, DIL, Short Sale, Modification, Note Sale)

#### Added `task_status_options()` View
- **Purpose**: Return active task types for sub-filter dropdown
- **Endpoint**: `GET /api/reporting/task-statuses/`
- **Query Param**: `?track=reo` (optional - filter by specific track)
- **Returns**: List of task status options with track association

### 4. Serializers (`serial_rep_filterOptions.py`)

#### Updated `StatusOptionSerializer`
- **Changed Purpose**: Now serializes track options instead of trade statuses
- **Fields**:
  - `value`: Track code (reo, fc, dil, short_sale, modification, note_sale)
  - `label`: Display label (REO, Foreclosure, DIL, etc.)
  - `count`: Number of assets on this track

#### Added `TaskStatusOptionSerializer`
- **Purpose**: Serialize task status options
- **Fields**:
  - `value`: Task type code (eviction, trashout, nod_noi, etc.)
  - `label`: Display label (Eviction, Trashout, NOD/NOI, etc.)
  - `track`: Track this task belongs to (reo, fc, dil, etc.)
  - `count`: Number of assets with this task

### 5. URLs (`urls.py`)

#### Updated Comments for `/api/reporting/statuses/`
- Now documented as "Track filter options (AM outcome tracks)"

#### Added `/api/reporting/task-statuses/`
- **Purpose**: Task status filter options endpoint
- **Query Params**: `?track=reo` (optional)
- **View**: `view_rep_filters.task_status_options`

## API Endpoints

### Filter Options Endpoints

```
GET /api/reporting/statuses/
Description: Get all AM outcome tracks
Returns: [
  {
    "value": "reo",
    "label": "REO",
    "count": 25
  },
  {
    "value": "fc",
    "label": "Foreclosure",
    "count": 15
  },
  ...
]
```

```
GET /api/reporting/task-statuses/
GET /api/reporting/task-statuses/?track=reo
Description: Get all active task types (optionally filtered by track)
Returns: [
  {
    "value": "eviction",
    "label": "Eviction",
    "track": "reo",
    "count": 10
  },
  {
    "value": "trashout",
    "label": "Trashout",
    "track": "reo",
    "count": 8
  },
  ...
]
```

### Query Parameters for Reporting Endpoints

**Old Query Params** (REMOVED):
```
?statuses=DD,AWARDED,PASS,BOARD
```

**New Query Params** (ADDED):
```
?tracks=reo,fc,dil
?task_statuses=eviction,trashout
```

**Example Full Query**:
```
GET /api/reporting/by-trade/?trade_ids=1,2,3&tracks=reo,fc&task_statuses=eviction
```

## Track & Task Mappings

### Outcome Tracks
| Value | Label | Related Name (AssetIdHub) |
|-------|-------|---------------------------|
| `reo` | REO | `reo_data` |
| `fc` | Foreclosure | `fc_sale` |
| `dil` | DIL | `dil` |
| `short_sale` | Short Sale | `short_sale` |
| `modification` | Modification | `modification` |
| `note_sale` | Note Sale | `note_sale` |

### Task Models & Related Names
| Track | Task Model | Related Name (AssetIdHub) |
|-------|------------|---------------------------|
| REO | `REOtask` | `reo_tasks` |
| FC | `FCTask` | `fc_tasks` |
| DIL | `DILTask` | `dil_tasks` |
| Short Sale | `ShortSaleTask` | `short_sale_tasks` |
| Modification | `ModificationTask` | `modification_tasks` |
| Note Sale | `NoteSaleTask` | `note_sale_tasks` |

### Example Task Types by Track

**REO Tasks**: eviction, trashout, renovation, marketing, under_contract, sold

**FC Tasks**: nod_noi, fc_filing, mediation, judgement, redemption, sale_scheduled, sold

**DIL Tasks**: pursuing_dil, owner_contacted, dil_failed, dil_drafted, dil_executed

**Short Sale Tasks**: list_price_accepted, listed, under_contract, sold

**Modification Tasks**: mod_drafted, mod_executed, mod_rpl, mod_failed, note_sale

**Note Sale Tasks**: potential_note_sale, out_to_market, pending_sale, sold

## Frontend Integration

### Status Filter (Tracks)
The "Statuses" filter dropdown should now show:
- REO
- Foreclosure
- DIL
- Short Sale
- Modification
- Note Sale

### Task Status Sub-Filter (NEW)
Add a new "Task Statuses" filter dropdown that shows:
- All active task types across all tracks
- Can be filtered by selected track(s) for better UX

### API Calls

```javascript
// Get track options
const tracks = await axios.get('/api/reporting/statuses/');

// Get all task options
const tasks = await axios.get('/api/reporting/task-statuses/');

// Get task options for specific track
const reoTasks = await axios.get('/api/reporting/task-statuses/?track=reo');

// Apply filters to reporting
const data = await axios.get('/api/reporting/by-trade/', {
  params: {
    tracks: 'reo,fc',
    task_statuses: 'eviction,trashout'
  }
});
```

## Notes

1. **Only Boarded Trades**: All filters still only show data for trades with status='BOARD' (as implemented earlier)

2. **OR Logic**: Multiple tracks or task statuses use OR logic (show assets on ANY selected track/task)

3. **Task Search Across All Models**: When filtering by task status, the system searches across all 6 task models to find matches

4. **Performance**: Uses optimized Q objects and database indexes for efficient filtering

5. **Backwards Compatibility**: Frontend must be updated to use new query parameters (`tracks` and `task_statuses` instead of `statuses`)

## Testing Checklist

- [ ] `/api/reporting/statuses/` returns track options with counts
- [ ] `/api/reporting/task-statuses/` returns all task options
- [ ] `/api/reporting/task-statuses/?track=reo` filters tasks by track
- [ ] Filtering by single track works
- [ ] Filtering by multiple tracks works (OR logic)
- [ ] Filtering by single task status works
- [ ] Filtering by multiple task statuses works (OR logic)
- [ ] Combining track + task filters works correctly
- [ ] All reporting endpoints (by-trade, by-status, summary) use new filters
- [ ] Frontend dropdowns show correct options
- [ ] Frontend sends correct query parameters

