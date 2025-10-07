# SellerRawData ETL System

## Quick Start

### 1. Install Dependencies
```bash
pip install pandas openpyxl xlrd
```

### 2. Set API Key (Already configured in .env)
Your `.env` file already contains:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 3. Run Import (Auto-Create Mode - Most Common)
```bash
# Simplest - auto-create seller and trade from filename
python manage.py import_seller_data --file data.xlsx --auto-create

# With custom seller name
python manage.py import_seller_data --file data.xlsx --seller-name "ABC Capital" --auto-create

# Or use existing seller/trade IDs
python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000
```

---

## What This Does

**Intelligent ETL Pipeline** for importing seller loan tape data from Excel/CSV files into the ProjectAlpha database.

**Key Features**:
- ✅ **AI-Powered Column Mapping** - Claude AI automatically maps source columns to database fields
- ✅ **Multi-Format Support** - Handles .xlsx, .xls, and .csv files
- ✅ **Type Conversion** - Automatic conversion of currency, dates, booleans
- ✅ **Validation** - Data quality checks before database insertion
- ✅ **Reusable Mappings** - Save and reuse column mappings across imports
- ✅ **Batch Processing** - Efficient bulk inserts with transaction safety
- ✅ **Dry Run Mode** - Preview imports before committing

---

## Files

### Command
- `projectalphav1/acq_module/management/commands/import_seller_data.py` - Main ETL command

### Documentation
- `Admin/DataUploads/ETL_INSTRUCTIONS.md` - Complete usage guide
- `Admin/DataUploads/README_ETL.md` - This file (quick reference)

### Configuration
- `Admin/DataUploads/example_mapping_config.json` - Template for custom column mappings

### Sample Data
- `Admin/DataUploads/seller_boarded_data_headers.csv` - Example of expected data format

---

## Common Commands

### Auto-Create Seller & Trade (NEW - Most Common Workflow)
```bash
# Simplest: Auto-create from filename
python manage.py import_seller_data \
    --file Admin/DataUploads/ABC_Capital_Q1_2025.xlsx \
    --auto-create

# With custom seller name
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape.xlsx \
    --seller-name "ABC Capital" \
    --auto-create

# Dry run first
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape.xlsx \
    --seller-name "ABC Capital" \
    --auto-create \
    --dry-run
```

### Use Existing Seller & Trade IDs
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape.xlsx \
    --seller-id 1000 \
    --trade-id 2000
```

### Save Mapping for Reuse
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --save-mapping Admin/DataUploads/seller_A_mapping.json
```

### Use Saved Mapping
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape_feb.xlsx \
    --seller-id 1000 \
    --trade-id 2001 \
    --config Admin/DataUploads/seller_A_mapping.json
```

### Import Specific Excel Sheet
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/workbook.xlsx \
    --sheet "Loan Tape" \
    --seller-id 1000 \
    --trade-id 2000
```

### Update Existing Records
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/updated_data.xlsx \
    --seller-id 1000 \
    --trade-id 2000 \
    --update-existing
```

### Skip AI Mapping (Exact Match Only)
```bash
python manage.py import_seller_data \
    --file Admin/DataUploads/loan_tape.csv \
    --seller-id 1000 \
    --trade-id 2000 \
    --no-ai
```

---

## How It Works

### Step 1: File Reading
Uses **pandas** library to read Excel (.xlsx, .xls) or CSV files with flexible parsing.

### Step 2: Column Mapping
Three mapping strategies:

1. **AI Mapping (Default)**: Claude AI analyzes column names and semantically maps to database fields
2. **Config Mapping**: Uses predefined JSON mapping file
3. **Exact Matching**: Direct column name to field name matching

### Step 3: Data Transformation
- Currency formatting: `$1,234.56` → `1234.56`
- Date parsing: `12/25/2024` → `2024-12-25`
- Boolean conversion: `yes` → `True`
- State normalization: `ca` → `CA`
- Auto-calculation: `total_debt`, `months_dlq`

### Step 4: Validation
- Required field checks (sellertape_id)
- Type validation
- Foreign key verification (Seller, Trade exist)

### Step 5: Database Insert
- **CRITICAL**: Creates AssetIdHub first (master asset identifier)
- Creates SellerRawData with asset_hub as primary key (1:1 relationship)
- Batch inserts for performance (default: 100 records per batch)
- Transaction safety (all-or-nothing per batch)
- Duplicate handling (skip or update based on sellertape_id)

---

## Architecture

### Data Flow
```
Email/Data Room/Upload
    ↓
Excel/CSV File
    ↓
Pandas DataFrame
    ↓
Claude AI Column Mapping
    ↓
Type Conversion & Validation
    ↓
AssetIdHub Creation
    ↓
SellerRawData Insert
    ↓
Database
```

### Key Models & Relationships
- **Seller** - Seller entity (1:many trades)
- **Trade** - Transaction/batch (1:many assets)
- **AssetIdHub** - Master asset identifier (created FIRST, auto-incrementing)
- **SellerRawData** - Raw seller tape data (uses AssetIdHub as primary_key via OneToOneField)

**CRITICAL Architecture Pattern**:
1. AssetIdHub created first → generates unique ID
2. SellerRawData created with asset_hub as PK (1:1 relationship)
3. All other asset tables reference the same hub (BlendedOutcomeModel, Valuations, etc.)
4. Hub ID is the master identifier across the entire system

### Technology Stack
- **Django Management Command** - CLI interface
- **Pandas** - Data reading and processing
- **Openpyxl** - Excel file parsing
- **Claude AI (Anthropic)** - Intelligent column mapping
- **PostgreSQL** - Database backend

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
**Solution**: Set environment variable or add to `.env` file
```bash
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### "Seller with ID X does not exist"
**Solution**: Create Seller in Django admin first
```bash
python manage.py createsuperuser  # If needed
# Then access http://localhost:8000/admin
```

### "File not found"
**Solution**: Use absolute path or verify relative path from project root
```bash
# Absolute path
python manage.py import_seller_data --file C:\full\path\to\file.xlsx ...

# Relative from project root
python manage.py import_seller_data --file Admin/DataUploads/file.xlsx ...
```

### Import is Slow
**Solution**: Increase batch size or disable AI mapping for subsequent imports
```bash
python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000 --batch-size 500
```

### Columns Not Mapping
**Solution**: Create manual mapping config
```bash
# First, run dry-run to see what AI mapped
python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000 --dry-run

# Create custom mapping based on example_mapping_config.json
# Then use it:
python manage.py import_seller_data --file data.xlsx --seller-id 1000 --trade-id 2000 --config my_mapping.json
```

---

## Dependencies

### Python Packages
```
pandas>=2.2.0,<3          # Data processing
openpyxl>=3.1.0,<4        # Excel support
xlrd>=2.0.0,<3            # Legacy .xls support
anthropic>=0.30,<1        # Claude AI integration
Django==5.2.5             # Web framework
psycopg2-binary==2.9.10   # PostgreSQL adapter
```

### External APIs
- **Anthropic Claude API** - For intelligent column mapping
  - Get API key: https://console.anthropic.com/
  - Pricing: https://www.anthropic.com/pricing
  - Model used: `claude-3-5-sonnet-20241022`

---

## Best Practices

### ✅ DO
- Always run `--dry-run` first on new data sources
- Save mappings for repeat sellers (`--save-mapping`)
- Validate source data quality before import
- Create Seller and Trade records in admin first
- Monitor error counts in output
- Check random sample in database after import

### ❌ DON'T
- Import without previewing (`--dry-run`)
- Ignore validation errors
- Import duplicate sellertape_ids without review
- Use same Trade ID for different seller tapes
- Skip data quality checks in source files

---

## Support & Documentation

### Full Documentation
See `Admin/DataUploads/ETL_INSTRUCTIONS.md` for comprehensive guide including:
- All command options
- Field definitions
- Data validation rules
- Workflow examples
- Troubleshooting guide

### Model Reference
See `projectalphav1/acq_module/models/seller.py` for:
- SellerRawData field definitions
- Data types and constraints
- Auto-calculated fields
- Business logic

### Code Reference
See `projectalphav1/acq_module/management/commands/import_seller_data.py` for:
- Implementation details
- Type conversion logic
- Validation rules
- AI prompt engineering

---

## Version History

### Version 1.0 (Current)
- Initial ETL system with AI-powered column mapping
- Support for Excel (.xlsx, .xls) and CSV files
- Intelligent type conversion and validation
- Batch processing with transaction safety
- Reusable mapping configurations
- Dry run mode for preview

### Roadmap
- [ ] Web-based upload interface
- [ ] Real-time import progress tracking
- [ ] Email inbox integration
- [ ] Data room connector
- [ ] Enhanced validation rules
- [ ] Import audit logging
- [ ] Mapping suggestion learning
