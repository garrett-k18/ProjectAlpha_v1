# StateBridge FTP Server ETL Process Documentation

## Overview

The StateBridge FTP ETL process automatically downloads, processes, and imports loan servicing data from StateBridge's FTPS server into the Project Alpha database. The system uses a raw data landing pattern where all incoming data is stored as strings in raw tables before being transformed and validated in downstream ETL processes.

## Architecture Pattern

### Raw Data Landing Pattern

**WHAT**: All StateBridge data is stored in raw landing tables with all fields as `CharField` to accept data exactly as received.

**WHY**: 
- Raw data may have formatting issues, invalid values, encoding problems
- Allows for data quality analysis before transformation
- Preserves original data for audit and troubleshooting

**HOW**: 
1. **Raw Landing Tables** (e.g., `SBDailyLoanData`, `EOMTrialBalanceData`) = Raw strings, no validation
2. **ETL Cleaning Process** = Parse, validate, transform
3. **Core Tables** (e.g., `ServicerLoanData`) = Typed fields with constraints

## FTP Connection Details

### Environment Variables

The ETL process requires the following environment variables:

- `STATEBRIDGE_FTPS_HOST` - FTPS server hostname
- `STATEBRIDGE_FTPS_USERNAME` - FTPS username
- `STATEBRIDGE_FTPS_PASSWORD` - FTPS password
- `STATEBRIDGE_FTPS_PORT` - FTPS port (default: 990)
- `STATEBRIDGE_FTPS_IMPLICIT` - Use implicit TLS (default: true)
- `STATEBRIDGE_FTPS_REMOTE_DIR` - Remote directory path (default: `/FirstLienCapital/To_FirstLienCapital`)

### Connection Type

The system uses **Implicit FTPS** (FTP over TLS) which requires TLS negotiation immediately after TCP connect, before the server sends the FTP welcome banner.

## File Processing Workflow

### 1. File Discovery

**Location**: `etl/management/commands/import_statebridge_from_ftps.py`

The system:
1. Connects to StateBridge FTPS server
2. Lists files in the remote directory
3. Filters files matching pattern: `FirstLienCapital_*.xlsx`
4. Optionally filters by file type (kind) using `--kind` parameter
5. Optionally selects only the latest file using `--latest-only` parameter

### 2. File Type Detection

Files are identified by their filename pattern:

| File Type | Filename Pattern | Model Class |
|-----------|-----------------|-------------|
| Loan Data | `*_loandata_*` | `SBDailyLoanData` |
| Foreclosure Data | `*_foreclosuredata_*` | `SBDailyForeclosureData` |
| Bankruptcy Data | `*_bankruptcydata_*` | `SBDailyBankruptcyData` |
| Comment Data | `*_commentdata_*` | `SBDailyCommentData` |
| Pay History | `*_payhistoryreport_*` | `SBDailyPayHistoryData` |
| Transaction Data | `*_transactiondata_*` | `SBDailyTransactionData` |
| ARM Data | `*_armdata_*` | `SBDailyArmData` |
| **EOM Trial Balance** | `*_trialbalancedata_*` or `*_eomtrialbalance_*` | `EOMTrialBalanceData` |
| **EOM Trust Tracking** | `*_trusttrackingdata_*` or `*_eomtrusttracking_*` | `EOMTrustTrackingData` |

### 3. Duplicate Detection

The system maintains a manifest file (`processed_manifest.json`) that tracks:
- Remote filename
- SHA256 hash of downloaded file
- Download timestamp
- Import results (rows read, rows inserted)
- Skip reports (if enabled)

Files are skipped if:
- Already processed (found in manifest)
- All rows are duplicates (based on unique constraints)

### 4. Data Import

**Location**: `etl/management/commands/import_statebridge_file.py`

The import process:
1. Reads Excel/CSV file using pandas
2. Normalizes column headers (converts to snake_case, removes special characters)
3. Maps columns to model fields
4. Extracts file date from filename (YYYYMMDD pattern)
5. Creates model instances with all fields as strings
6. Bulk inserts in batches (default: 2000 rows per batch)
7. Uses `ignore_conflicts=True` to handle duplicates gracefully

## Raw Data Models

### Daily Data Models

These models store daily snapshots of loan data:

1. **SBDailyLoanData** - Complete loan snapshot with all loan characteristics
2. **SBDailyArmData** - ARM-specific loan data
3. **SBDailyForeclosureData** - Foreclosure process tracking
4. **SBDailyBankruptcyData** - Bankruptcy case tracking
5. **SBDailyCommentData** - Loan comments and notes
6. **SBDailyPayHistoryData** - Payment history (last 13 months)
7. **SBDailyTransactionData** - Individual transaction records

### End of Month (EOM) Data Models

These models store end-of-month summary data:

#### EOMTrialBalanceData

**WHAT**: End-of-month trial balance data showing loan balances and status at month-end.

**WHY**: Provides monthly snapshot of all loan balances, fees, and status for reconciliation and reporting.

**HOW**: Stores raw data from StateBridge EOM trial balance reports.

**File Pattern**: `FirstLienCapital_*_trialbalancedata_*.xlsx` or `FirstLienCapital_*_eomtrialbalance_*.xlsx`

**Fields**:
- `loan_id` - Loan identifier (CharField, max_length=50)
- `investor_id` - Investor identifier (CharField, max_length=50)
- `borrower_name` - Borrower full name (CharField, max_length=150)
- `principal_bal` - Principal balance (CharField, max_length=50)
- `escrow_bal` - Escrow balance (CharField, max_length=50)
- `other_funds_bal` - Other funds balance (CharField, max_length=50)
- `late_charge_bal` - Late charge balance (CharField, max_length=50)
- `legal_fee_bal` - Legal fee balance (CharField, max_length=50)
- `deferred_prin` - Deferred principal (CharField, max_length=50)
- `primary_status` - Primary loan status (CharField, max_length=50)
- `investor_loan_id` - Investor loan identifier (CharField, max_length=50)
- `loan_type` - Type of loan (CharField, max_length=50)
- `due_date` - Next payment due date (CharField, max_length=20)
- `unapplied_bal` - Unapplied balance (CharField, max_length=50)
- `loss_draft_bal` - Loss draft balance (CharField, max_length=50)
- `asst_bal` - Asset balance (CharField, max_length=50)
- `nsf_fee_bal` - NSF fee balance (CharField, max_length=50)
- `oth_fee_bal` - Other fee balance (CharField, max_length=50)
- `deferred_int` - Deferred interest (CharField, max_length=50)
- `date_inactive` - Date loan became inactive (CharField, max_length=20)
- `legal_status` - Legal status code (CharField, max_length=50)
- `warning_status` - Warning status code (CharField, max_length=50)

**Unique Constraint**: TBD - Needs to be defined based on business requirements (likely `file_date` + `loan_id`)

**Indexes**: TBD - Should include indexes on:
- `loan_id` (for lookups)
- `investor_id` (for filtering)
- `file_date` (for date-based queries)
- `primary_status` (for status filtering)

#### EOMTrustTrackingData

**WHAT**: End-of-month trust tracking data showing payments received, collected, and payoff information.

**WHY**: Tracks monthly payment collections, interest collected, and payoff activity for trust accounting and reconciliation.

**HOW**: Stores raw data from StateBridge EOM trust tracking reports.

**File Pattern**: `FirstLienCapital_*_trusttrackingdata_*.xlsx` or `FirstLienCapital_*_eomtrusttracking_*.xlsx`

**Fields**:
- `loan_id` - Loan identifier (CharField, max_length=50)
- `investor_loan_id` - Investor loan identifier (CharField, max_length=50)
- `received_date` - Date payment was received (CharField, max_length=20)
- `due_date` - Payment due date (CharField, max_length=20)
- `principal_paid_off` - Principal amount paid off (CharField, max_length=50)
- `interest_collected` - Interest amount collected (CharField, max_length=50)
- `sf_collected` - Servicing fee collected (CharField, max_length=50)
- `net_interest` - Net interest amount (CharField, max_length=50)
- `description` - Transaction description (CharField, max_length=200)
- `payoff_reason` - Reason for payoff if applicable (CharField, max_length=100)

**Unique Constraint**: TBD - Needs to be defined based on business requirements (likely `file_date` + `loan_id` + `received_date` or similar)

**Indexes**: TBD - Should include indexes on:
- `loan_id` (for lookups)
- `investor_loan_id` (for investor-based queries)
- `received_date` (for date-based queries)
- `due_date` (for payment tracking)

## Integration Requirements

### 1. Update File Type Detection

**File**: `etl/management/commands/import_statebridge_from_ftps.py`

Add to `_matches_kind()` function:

```python
kind_aliases = {
    # ... existing aliases ...
    "eom_trial_balance": {"eom_trial_balance", "trialbalance", "trialbalancedata", "eomtrialbalance"},
    "eom_trust_tracking": {"eom_trust_tracking", "trusttracking", "trusttrackingdata", "eomtrusttracking"},
}

# In the return statement:
{
    # ... existing mappings ...
    "eom_trial_balance": "_trialbalancedata_" in name or "_eomtrialbalance_" in name,
    "eom_trust_tracking": "_trusttrackingdata_" in name or "_eomtrusttracking_" in name,
}
```

### 2. Update Model Mapping

**File**: `etl/management/commands/import_statebridge_file.py`

Add to `_infer_kind_from_filename()` function:

```python
if "_trialbalancedata_" in name or "_eomtrialbalance_" in name:
    return "eom_trial_balance"
if "_trusttrackingdata_" in name or "_eomtrusttracking_" in name:
    return "eom_trust_tracking"
```

Add to `_model_for_kind()` function:

```python
from etl.models import (
    # ... existing imports ...
    EOMTrialBalanceData,
    EOMTrustTrackingData,
)

return {
    # ... existing mappings ...
    "eom_trial_balance": EOMTrialBalanceData,
    "eom_trust_tracking": EOMTrustTrackingData,
}[kind]
```

### 3. Define Unique Constraints

**File**: `etl/models/model_etl_statebridge_raw.py`

Add `Meta` classes to both models with appropriate unique constraints and indexes:

**EOMTrialBalanceData**:
```python
class Meta:
    db_table = 'eom_trial_balance_records'
    verbose_name = 'StateBridge EOM Trial Balance Data'
    verbose_name_plural = 'StateBridge EOM Trial Balance Data'
    
    indexes = [
        models.Index(fields=['loan_id'], name='eom_trial_loan_id_idx'),
        models.Index(fields=['investor_id'], name='eom_trial_investor_id_idx'),
        models.Index(fields=['file_date'], name='eom_trial_file_date_idx'),
        models.Index(fields=['primary_status'], name='eom_trial_status_idx'),
        models.Index(fields=['loan_id', 'file_date'], name='eom_trial_loan_date_idx'),
    ]
    
    constraints = [
        models.UniqueConstraint(
            fields=['file_date', 'loan_id'],
            name='uniq_eom_trial_fdate_loanid',
            condition=models.Q(file_date__isnull=False)
            & ~models.Q(file_date="")
            & models.Q(loan_id__isnull=False)
            & ~models.Q(loan_id=""),
        ),
    ]
```

**EOMTrustTrackingData**:
```python
class Meta:
    db_table = 'eom_trust_tracking_records'
    verbose_name = 'StateBridge EOM Trust Tracking Data'
    verbose_name_plural = 'StateBridge EOM Trust Tracking Data'
    
    indexes = [
        models.Index(fields=['loan_id'], name='eom_trust_loan_id_idx'),
        models.Index(fields=['investor_loan_id'], name='eom_trust_investor_loan_id_idx'),
        models.Index(fields=['received_date'], name='eom_trust_received_date_idx'),
        models.Index(fields=['due_date'], name='eom_trust_due_date_idx'),
        models.Index(fields=['loan_id', 'received_date'], name='eom_trust_loan_received_idx'),
    ]
    
    constraints = [
        models.UniqueConstraint(
            fields=['file_date', 'loan_id', 'received_date'],
            name='uniq_eom_trust_fdate_loanid_recd',
            condition=models.Q(file_date__isnull=False)
            & ~models.Q(file_date="")
            & models.Q(loan_id__isnull=False)
            & ~models.Q(loan_id="")
            & models.Q(received_date__isnull=False)
            & ~models.Q(received_date=""),
        ),
    ]
```

**Note**: Both models need a `file_date` field added to support the unique constraints and date-based queries.

### 4. Add file_date Field

Both models need a `file_date` field to track when the data was extracted:

```python
# Add to EOMTrialBalanceData
file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)

# Add to EOMTrustTrackingData  
file_date = models.CharField(max_length=20, null=True, blank=True, db_index=True)
```

### 5. Update Unique Key Detection

**File**: `etl/management/commands/import_statebridge_file.py`

Add to `_unique_key_fields_for_model()` function:

```python
if model is EOMTrialBalanceData:
    return ("file_date", "loan_id")
if model is EOMTrustTrackingData:
    return ("file_date", "loan_id", "received_date")
```

Add to `_existing_keys_in_db()` function:

```python
if model is EOMTrialBalanceData:
    loan_ids = {k[1] for k in keys_in_file_unique}
    existing = model.objects.filter(
        file_date=file_date_iso, 
        loan_id__in=loan_ids
    ).values_list("file_date", "loan_id")
    return set(tuple(row) for row in existing)

if model is EOMTrustTrackingData:
    loan_ids = {k[1] for k in keys_in_file_unique}
    existing = model.objects.filter(
        file_date=file_date_iso, 
        loan_id__in=loan_ids
    ).values_list("file_date", "loan_id", "received_date")
    return set(tuple(row) for row in existing)
```

### 6. Add Metadata Fields

Both models should have `created_at` and `updated_at` fields for audit tracking:

```python
# Add to both models
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

## Usage Examples

### Download and Import Latest EOM Trial Balance File

```bash
python manage.py import_statebridge_from_ftps \
    --kind eom_trial_balance \
    --latest-only \
    --batch-size 2000
```

### Download and Import Latest EOM Trust Tracking File

```bash
python manage.py import_statebridge_from_ftps \
    --kind eom_trust_tracking \
    --latest-only \
    --batch-size 2000
```

### Import Specific File Locally

```bash
python manage.py import_statebridge_file \
    --file /path/to/FirstLienCapital_20240131_trialbalancedata_20240131.xlsx \
    --batch-size 2000 \
    --report-skips
```

### Dry Run (Test Without Importing)

```bash
python manage.py import_statebridge_from_ftps \
    --kind eom_trial_balance \
    --dry-run \
    --report-skips
```

## Data Flow

```
StateBridge FTPS Server
    ↓
[import_statebridge_from_ftps.py]
    - Connects to FTPS
    - Downloads files
    - Tracks in manifest
    ↓
[import_statebridge_file.py]
    - Reads Excel/CSV
    - Normalizes headers
    - Maps to model fields
    - Bulk inserts
    ↓
Raw Landing Tables
    - EOMTrialBalanceData
    - EOMTrustTrackingData
    ↓
[Future: ETL Transformation Service]
    - Data validation
    - Type conversion
    - Business rule application
    ↓
Core Tables
    - (To be defined)
```

## Error Handling

### Duplicate Detection

- Files are tracked in `processed_manifest.json` by filename
- Rows are checked for duplicates using unique constraints
- Duplicate files are skipped automatically
- Duplicate rows are ignored using `ignore_conflicts=True`

### Validation

- All fields are stored as strings (CharField) to accept any value
- No validation occurs at import time
- Validation should occur in downstream ETL processes

### Logging

- Import results are logged to stdout as JSON
- Skip reports can be enabled with `--report-skips`
- Errors are captured and reported in the output payload

## Maintenance

### Manifest Management

The `processed_manifest.json` file tracks processed files. To reprocess a file:

1. Remove entry from manifest, OR
2. Use `--force` flag to ignore manifest

### Database Cleanup

To remove old data:

```python
# Remove data older than 90 days
from datetime import datetime, timedelta
from etl.models import EOMTrialBalanceData, EOMTrustTrackingData

cutoff_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

EOMTrialBalanceData.objects.filter(file_date__lt=cutoff_date).delete()
EOMTrustTrackingData.objects.filter(file_date__lt=cutoff_date).delete()
```

## Testing

### Unit Tests

Create tests in `etl/tests/test_models.py`:

```python
def test_eom_trial_balance_model():
    """Test EOMTrialBalanceData model creation"""
    data = EOMTrialBalanceData.objects.create(
        file_date='2024-01-31',
        loan_id='12345',
        investor_id='INV001',
        borrower_name='John Doe',
        principal_bal='100000.00',
    )
    assert data.loan_id == '12345'

def test_eom_trust_tracking_model():
    """Test EOMTrustTrackingData model creation"""
    data = EOMTrustTrackingData.objects.create(
        file_date='2024-01-31',
        loan_id='12345',
        investor_loan_id='INV-12345',
        received_date='2024-01-15',
        principal_paid_off='500.00',
    )
    assert data.loan_id == '12345'
```

### Integration Tests

Test the full import workflow:

```python
def test_eom_trial_balance_import():
    """Test importing EOM trial balance file"""
    file_path = Path('test_data/eom_trial_balance.xlsx')
    result = import_statebridge_file(
        file_path,
        dry_run=False,
        batch_size=100,
    )
    assert result.model_name == 'EOMTrialBalanceData'
    assert result.rows_inserted > 0
```

## Future Enhancements

1. **ETL Transformation Service**: Create service to transform raw EOM data to core tables
2. **Data Quality Checks**: Add validation rules for EOM data
3. **Reconciliation Reports**: Generate reports comparing EOM data to daily snapshots
4. **Automated Scheduling**: Set up cron jobs or scheduled tasks for automatic imports
5. **Alerting**: Notify on import failures or data quality issues

## Notes

- All date fields are stored as strings in YYYY-MM-DD format (extracted from filename)
- All numeric fields are stored as strings to preserve original formatting
- File dates are extracted from filename pattern (YYYYMMDD)
- The system supports both Excel (.xlsx, .xls) and CSV file formats
- Batch size defaults to 2000 rows but can be adjusted based on system performance
