# SellerRawData ETL Instructions

## Overview

This document provides step-by-step instructions for importing seller data from Excel/CSV files into the ProjectAlpha database using the intelligent ETL system.

**WHAT**: Instructions for data import workflows  
**WHY**: Standardize data intake from multiple sources (email, manual upload, data rooms)  
**WHERE**: Use for all seller data imports into SellerRawData model  
**HOW**: Command-line tool with AI-powered column mapping

---

## Prerequisites

### 1. Required Software
- Python 3.10+
- Django environment configured
- Access to ProjectAlpha database

### 2. Required API Keys
```bash
# Set in your environment or .env file
ANTHROPIC_API_KEY=sk-ant-...your-api-key-here...
```

### 3. Database Setup
- **NEW**: No pre-setup required! Use `--auto-create` to auto-generate Seller and Trade
- **OR** create Seller and Trade in Django admin first (for manual control)

---

## Import Workflows

### Workflow 1: Email Inbox → Database (Auto-Create - RECOMMENDED)

**Use Case**: Seller sends Excel file via email

**Steps**:
1. Download attachment from email to `Admin/DataUploads/` folder
2. Run import command with `--auto-create`:
   ```bash
   # Auto-create seller and trade
   python manage.py import_seller_data \
       --file Admin/DataUploads/ABC_Capital_Jan2025.xlsx \
       --seller-name "ABC Capital" \
       --auto-create \
       --dry-run
   ```
3. Review AI-generated column mapping and preview
4. Run live import (remove `--dry-run`)
5. Verify import success in Django admin

**Tips**:
- Use `--dry-run` first to preview
- Seller name can be extracted from filename if not specified
- Save mapping with `--save-mapping` for future imports from same seller
- System auto-generates Trade name with date

---

### Workflow 2: Manual Upload → Database

**Use Case**: User uploads file through web interface (future feature)

**Steps**:
1. User selects file via frontend upload form
2. Backend receives file and saves to temp location
3. Backend calls ETL command programmatically
4. Returns import summary to frontend

**Future Implementation**:
```python
# In Django view
from django.core.management import call_command

result = call_command(
    'import_seller_data',
    file=uploaded_file.path,
    seller_id=seller_id,
    trade_id=trade_id,
    dry_run=False
)
```

---

### Workflow 3: Data Room → Database

**Use Case**: Bulk import from data room with multiple files

**Steps**:
1. Download all files from data room to local folder
2. Create mapping config for consistent column mapping:
   ```bash
   # First file - let AI generate mapping
   python manage.py import_seller_data \
       --file tape1.xlsx \
       --seller-id 1000 \
       --trade-id 2000 \
       --save-mapping mapping_config.json
   ```
3. Use saved mapping for remaining files:
   ```bash
   python manage.py import_seller_data \
       --file tape2.xlsx \
       --seller-id 1000 \
       --trade-id 2001 \
       --config mapping_config.json
   
   python manage.py import_seller_data \
       --file tape3.xlsx \
       --seller-id 1000 \
       --trade-id 2002 \
       --config mapping_config.json
   ```

**Tips**:
- Use same mapping config when seller provides consistent format
- Process in batches of 100-500 records for optimal performance
- Monitor database disk space for large imports

---

## Command Reference

### Basic Import (Auto-Create - RECOMMENDED)
```bash
# Simplest - auto-create from filename
python manage.py import_seller_data \
    --file path/to/ABC_Capital_2025.xlsx \
    --auto-create

# With custom seller name
python manage.py import_seller_data \
    --file path/to/file.xlsx \
    --seller-name "ABC Capital" \
    --auto-create
```

### Import with Existing Seller/Trade
```bash
python manage.py import_seller_data \
    --file path/to/file.xlsx \
    --seller-id 1000 \
    --trade-id 2000
```

### Advanced Options

#### Dry Run (Preview Only)
```bash
python manage.py import_seller_data \
    --file data.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --dry-run
```

#### Use Predefined Mapping
```bash
python manage.py import_seller_data \
    --file data.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --config mapping_config.json
```

#### Save Mapping for Reuse
```bash
python manage.py import_seller_data \
    --file data.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --save-mapping seller_A_mapping.json
```

#### Skip AI Mapping (Exact Match Only)
```bash
python manage.py import_seller_data \
    --file data.csv \
    --seller-id 1000 \
    --trade-id 2000 \
    --no-ai
```

#### Excel-Specific Options
```bash
python manage.py import_seller_data \
    --file workbook.xlsx \
    --sheet "Loan Tape" \
    --skip-rows 2 \
    --seller-id 1000 \
    --trade-id 2000
```

#### Update Existing Records
```bash
python manage.py import_seller_data \
    --file updated_data.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --update-existing
```

#### Large File Import
```bash
python manage.py import_seller_data \
    --file large_tape.csv \
    --seller-id 1000 \
    --trade-id 2000 \
    --batch-size 500
```

---

## Column Mapping

### How AI Mapping Works

The ETL system uses Claude AI (Sonnet 3.5) to intelligently map source columns to database fields.

**Example Mappings**:
- "Loan Balance" → `current_balance`
- "UPB" → `current_balance` (Unpaid Principal Balance)
- "Property Address" → `street_address`
- "Prop Type" → `property_type`
- "Borrower Last Name" → `borrower1_last`
- "Seller BPO" → `seller_asis_value`
- "FC Start Date" → `fc_first_legal_date`

### Manual Mapping Configuration

Create a JSON file to define exact mappings:

**Example: `mapping_config.json`**
```json
{
  "version": "1.0",
  "description": "Mapping for ABC Capital loan tapes",
  "column_mapping": {
    "Loan ID": "sellertape_id",
    "Alternative ID": "sellertape_altid",
    "Loan Status": "asset_status",
    "Street": "street_address",
    "City": "city",
    "State": "state",
    "Zip Code": "zip",
    "Property Type": "property_type",
    "Current UPB": "current_balance",
    "Total Debt": "total_debt",
    "Interest Rate": "interest_rate",
    "Seller As-Is Value": "seller_asis_value",
    "Seller ARV": "seller_arv_value",
    "Borrower Last": "borrower1_last",
    "Borrower First": "borrower1_first"
  }
}
```

---

## Target Database Fields

### SellerRawData Model Fields

**Required Fields**:
- `sellertape_id` (Integer) - Unique identifier from seller's tape
- `seller` (Foreign Key) - Links to Seller model
- `trade` (Foreign Key) - Links to Trade model

**Property Information**:
- `street_address` (Text)
- `city` (Text)
- `state` (Text) - Normalized to uppercase
- `zip` (Text)
- `property_type` (Choice) - SFR, Manufactured, Condo, 2-4 Family, Land, Multifamily 5+, Industrial, Mixed Use, Storage
- `product_type` (Choice) - BPL, HECM, VA, Conv, Commercial
- `occupancy` (Choice) - Vacant, Occupied, Unknown
- `year_built` (Integer)
- `sq_ft` (Integer)
- `lot_size` (Integer)
- `beds` (Integer)
- `baths` (Integer)

**Loan Financials**:
- `current_balance` (Decimal)
- `deferred_balance` (Decimal)
- `interest_rate` (Decimal)
- `original_balance` (Decimal)
- `original_rate` (Decimal)
- `default_rate` (Decimal)
- `accrued_note_interest` (Decimal)
- `accrued_default_interest` (Decimal)
- `escrow_balance` (Decimal)
- `escrow_advance` (Decimal)
- `recoverable_corp_advance` (Decimal)
- `late_fees` (Decimal)
- `other_fees` (Decimal)
- `suspense_balance` (Decimal)
- `total_debt` (Decimal) - Auto-calculated if not provided

**Dates**:
- `as_of_date` (Date)
- `next_due_date` (Date)
- `last_paid_date` (Date)
- `first_pay_date` (Date)
- `origination_date` (Date)
- `original_maturity_date` (Date)
- `current_maturity_date` (Date)

**Valuations**:
- `origination_value` (Decimal)
- `origination_arv` (Decimal)
- `origination_value_date` (Date)
- `seller_value_date` (Date)
- `seller_arv_value` (Decimal)
- `seller_asis_value` (Decimal)
- `additional_asis_value` (Decimal)
- `additional_arv_value` (Decimal)
- `additional_value_date` (Date)

**Foreclosure Information**:
- `fc_flag` (Boolean)
- `fc_first_legal_date` (Date)
- `fc_referred_date` (Date)
- `fc_judgement_date` (Date)
- `fc_scheduled_sale_date` (Date)
- `fc_sale_date` (Date)
- `fc_starting` (Decimal)

**Bankruptcy Information**:
- `bk_flag` (Boolean)
- `bk_chapter` (Text)

**Modification Information**:
- `mod_flag` (Boolean)
- `mod_date` (Date)
- `mod_maturity_date` (Date)
- `mod_term` (Integer)
- `mod_rate` (Decimal)
- `mod_initial_balance` (Decimal)

**Borrower Information**:
- `borrower1_last` (Text)
- `borrower1_first` (Text)
- `borrower2_last` (Text)
- `borrower2_first` (Text)

**Other**:
- `sellertape_altid` (Integer) - Alternative/secondary ID
- `asset_status` (Choice) - NPL, REO, PERF, RPL
- `months_dlq` (Integer) - Auto-calculated if not provided
- `current_term` (Integer)
- `original_term` (Integer)

---

## Database Architecture

### AssetIdHub Creation (CRITICAL)

**Every import creates AssetIdHub records first**:

1. **AssetIdHub** is created for each new asset (auto-incrementing ID)
2. **SellerRawData** uses this hub as its primary key (OneToOneField with primary_key=True)
3. This ensures every asset has a unique master identifier
4. All related tables (valuations, outcomes, cash flows) reference the same hub

**Example Flow**:
```
Import 100 records →
  Creates 100 AssetIdHub records (IDs: 1001-1100) →
    Creates 100 SellerRawData records (PKs: 1001-1100 via asset_hub)
```

**Why This Matters**:
- Asset Hub ID is the single source of truth across all tables
- No standard `id` field on SellerRawData - use `asset_hub_id` instead
- References: `srd.asset_hub_id` NOT `srd.id` (will crash)

---

## Data Validation Rules

### Automatic Conversions

**Currency Fields**:
- Strips `$` and `,` characters
- Converts to Decimal type
- Example: `$1,234,567.89` → `1234567.89`

**Date Fields**:
- Accepts multiple formats: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD-MMM-YYYY`
- Uses pandas date parsing for flexibility
- Example: `12/25/2024` or `2024-12-25` → `2024-12-25`

**Boolean Fields**:
- Accepts: `true`, `True`, `t`, `yes`, `y`, `1` → `True`
- Accepts: `false`, `False`, `f`, `no`, `n`, `0` → `False`

**State Field**:
- Auto-normalized to uppercase at model level
- Example: `ca` → `CA`

**Total Debt**:
- Auto-calculated from component fields if not provided
- Sum of: current_balance + deferred_balance + accrued_note_interest + escrow_advance + escrow_balance + recoverable_corp_advance + late_fees + other_fees + suspense_balance

**Months DLQ**:
- Auto-calculated from as_of_date and next_due_date if not provided

### Validation Errors

Common errors and solutions:

**Error: "Missing required field: sellertape_id"**
- Solution: Ensure source file has a column that maps to `sellertape_id`

**Error: "Seller with ID X does not exist"**
- Solution: Create Seller in Django admin first

**Error: "Trade with ID X does not exist"**
- Solution: Create Trade in Django admin first

**Error: "File not found"**
- Solution: Check file path, use absolute or relative path from project root

---

## Troubleshooting

### AI Mapping Not Working

**Symptoms**: Falls back to exact matching  
**Causes**:
- Missing `ANTHROPIC_API_KEY` environment variable
- Invalid or expired API key
- Network connectivity issues

**Solutions**:
1. Verify API key is set: `echo $ANTHROPIC_API_KEY` (Linux/Mac) or `echo %ANTHROPIC_API_KEY%` (Windows)
2. Test API key with simple request
3. Use `--config` with predefined mapping as workaround
4. Use `--no-ai` flag to skip AI mapping

### Import Slow for Large Files

**Solutions**:
- Increase batch size: `--batch-size 500`
- Disable AI mapping for subsequent imports: `--config mapping.json`
- Consider splitting file into smaller chunks
- Run during off-peak hours

### Duplicate Records

**Symptoms**: "Skipped: X records"  
**Cause**: Records with same sellertape_id already exist

**Solutions**:
- Review existing data before import
- Use `--update-existing` to update instead of skip
- Clean duplicates in source file first

### Column Not Mapping

**Symptoms**: Data not importing for specific field  
**Solutions**:
1. Check AI-generated mapping output
2. Create manual mapping config with exact column name
3. Verify column exists in source file (check for typos, extra spaces)
4. Check field name against SellerRawData model

---

## Best Practices

### 1. Always Dry Run First
```bash
# Preview before importing
python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000 --dry-run
```

### 2. Save Mappings for Repeat Sellers
```bash
# First import - save mapping
python manage.py import_seller_data --file seller_A_jan.xlsx --seller-id 1000 --trade-id 2000 --save-mapping seller_A_mapping.json

# Future imports - reuse mapping
python manage.py import_seller_data --file seller_A_feb.xlsx --seller-id 1000 --trade-id 2001 --config seller_A_mapping.json
```

### 3. Validate Source Data First
- Check for required columns (especially sellertape_id)
- Remove duplicate rows
- Verify date formats are consistent
- Ensure numeric fields don't have text

### 4. Create Seller and Trade First
- Use Django admin to create Seller and Trade records
- Note the IDs for use in import command
- Verify trade is linked to correct seller

### 5. Monitor Import Results
- Review "Errors" count in output
- Check first few errors for patterns
- Verify random sample in Django admin after import

### 6. Document Custom Mappings
- Add description to mapping JSON files
- Note seller name and date range
- Include example row from source file

---

## Support

**Issues or Questions**:
- Check Django logs for detailed error messages
- Review this documentation
- Consult SellerRawData model definition
- Test with sample data first

**Enhancement Requests**:
- Additional validation rules
- New data sources
- Custom transformations
- Performance optimizations
