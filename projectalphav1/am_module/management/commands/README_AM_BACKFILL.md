# AM Tracks and Tasks Backfill Guide

## Overview
The `import_am_tracks_and_tasks_backfill.py` command imports AM track outcomes and their tasks from a CSV file using `servicer_id` to match loans.

## Updated Track Support
✅ All tracks now supported:
- `fc` - Foreclosure
- `reo` - Real Estate Owned (updated with pre_marketing and listed)
- `dil` - Deed in Lieu
- `short_sale` - Short Sale
- `modification` - Loan Modification
- `note_sale` - Note Sale
- `performing` - Performing Track (NEW)
- `delinquent` - Delinquent Track (NEW)

## CSV Format

### Required Columns
- `servicer_id` - The loan's servicer ID (matches AssetIdHub)
- `track` - The track type (see list above)
- `task_type` - The task category (see valid values below)

### Optional Columns
- `task_started` - Date in YYYY-MM-DD format

### Example CSV Structure
```csv
servicer_id,track,task_type,task_started
123456,reo,eviction,2024-01-15
123456,reo,trashout,2024-01-20
123456,reo,pre_marketing,2024-02-15
123456,reo,listed,2024-03-01
789012,fc,nod_noi,2024-01-10
789012,fc,fc_filing,2024-02-01
345678,performing,perf,2024-01-01
345678,performing,rpl,2024-03-15
```

## Multiple Tracks for Same Loan

**YES - Just list each track/task combination on a separate row!**

The command uses `update_or_create()` which means:
- **Same loan + same track + same task_type** = Updates existing task
- **Same loan + same track + different task_type** = Creates new task
- **Same loan + different track** = Creates new track outcome

### Example: Loan with Multiple Tracks
```csv
servicer_id,track,task_type,task_started
100001,delinquent,dq_30,2024-01-01
100001,delinquent,dq_60,2024-02-01
100001,delinquent,dq_90,2024-03-01
100001,fc,nod_noi,2024-03-15
100001,fc,fc_filing,2024-04-01
100001,dil,pursuing_dil,2024-04-15
```

This creates:
- 1 DelinquentTrack with 3 tasks (dq_30, dq_60, dq_90)
- 1 FCSale with 2 tasks (nod_noi, fc_filing)
- 1 DIL with 1 task (pursuing_dil)

All linked to the same loan (servicer_id: 100001).

## Valid Task Types by Track

### REO (Real Estate Owned) - UPDATED
```
eviction
trashout
renovation
pre_marketing  ← NEW (replaces 'marketing')
listed         ← NEW
under_contract
sold
```

### FC (Foreclosure)
```
nod_noi
fc_filing
mediation
judgement
redemption
sale_scheduled
sold
```

### DIL (Deed in Lieu)
```
pursuing_dil
owner_contacted
dil_failed
dil_drafted
dil_executed
```

### Short Sale
```
list_price_accepted
listed
under_contract
sold
```

### Modification
```
mod_drafted
mod_executed
mod_rpl
mod_failed
note_sale
```

### Note Sale
```
potential_note_sale
out_to_market
pending_sale
sold
```

### Performing Track - NEW
```
perf
rpl
note_sold
```

### Delinquent Track - NEW
```
dq_30
dq_60
dq_90
dq_120_plus
loss_mit
fc_dil
```

## Command Usage

### Basic Import
```bash
python manage.py import_am_tracks_and_tasks_backfill --csv-file path/to/your/file.csv
```

### Dry Run (Preview without saving)
```bash
python manage.py import_am_tracks_and_tasks_backfill --csv-file path/to/your/file.csv --dry-run
```

### With Custom Batch Size
```bash
python manage.py import_am_tracks_and_tasks_backfill --csv-file path/to/your/file.csv --batch-size 500
```

### Target Specific Database
```bash
# Use production database
python manage.py import_am_tracks_and_tasks_backfill --csv-file path/to/your/file.csv --prod

# Use dev database
python manage.py import_am_tracks_and_tasks_backfill --csv-file path/to/your/file.csv --dev
```

## Important Notes

1. **Idempotent**: Safe to run multiple times - won't create duplicates
2. **One task per type per track**: Each loan can only have ONE task of each type per track
3. **Multiple tracks OK**: Same loan can have multiple different tracks
4. **Task updates**: If task already exists, it updates the `task_started` date
5. **Auto-creates tracks**: If track doesn't exist for the loan, it's created automatically

## Output Stats
The command reports:
- Processed: Total rows processed
- Tracks created: New track outcomes created
- Tasks created: New tasks created
- Tasks updated: Existing tasks updated
- Not Found: Loans not found by servicer_id
- Skipped invalid: Rows with missing required fields
- Errors: Rows that failed to process

## Common Scenarios

### Scenario 1: Backfill REO workflow
```csv
servicer_id,track,task_type,task_started
100001,reo,eviction,2024-01-15
100001,reo,trashout,2024-01-20
100001,reo,renovation,2024-02-01
100001,reo,pre_marketing,2024-02-15
100001,reo,listed,2024-03-01
100001,reo,under_contract,2024-03-15
100001,reo,sold,2024-04-01
```

### Scenario 2: Loan moved from Delinquent to FC to DIL
```csv
servicer_id,track,task_type,task_started
200002,delinquent,dq_30,2024-01-01
200002,delinquent,dq_60,2024-02-01
200002,delinquent,dq_90,2024-03-01
200002,fc,nod_noi,2024-03-15
200002,fc,fc_filing,2024-04-01
200002,dil,pursuing_dil,2024-04-15
200002,dil,owner_contacted,2024-05-01
200002,dil,dil_drafted,2024-05-15
```

### Scenario 3: Performing loan that went to Note Sale
```csv
servicer_id,track,task_type,task_started
300003,performing,perf,2024-01-01
300003,performing,rpl,2024-03-01
300003,note_sale,potential_note_sale,2024-06-01
300003,note_sale,out_to_market,2024-06-15
300003,note_sale,sold,2024-07-01
```

## Troubleshooting

**Error: "CSV missing required columns"**
- Ensure your CSV has headers: `servicer_id`, `track`, `task_type`

**Error: "No rows found in CSV"**
- Check file path is correct
- Ensure CSV has data rows (not just headers)

**High "Not Found" count**
- Servicer IDs don't match AssetIdHub records
- Check for leading/trailing spaces in servicer_id column

**High "Skipped invalid" count**
- Rows have empty required fields
- Check for blank cells in servicer_id, track, or task_type columns

**Invalid task_type errors**
- Task type doesn't match the track's allowed values
- Check spelling and use exact values from lists above (all lowercase, underscores)
