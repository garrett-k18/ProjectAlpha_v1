# Quick Test Guide

## Test the ETL System (Auto-Create Mode)

### Step 1: Verify Dependencies Installed ✅
```bash
python -c "import pandas; import openpyxl; import anthropic; print('✓ All packages ready')"
```

### Step 2: Test with Sample Data (Dry Run)
```bash
# Navigate to project root
cd c:\Users\garre\ProjectAlpha_v1\projectalphav1

# Run dry-run import with auto-create
python manage.py import_seller_data \
    --file ..\Admin\DataUploads\seller_boarded_data_headers.csv \
    --seller-name "Test Seller FLC" \
    --auto-create \
    --dry-run
```

**Expected Output:**
```
✓ Created new Seller: Test Seller FLC (ID: X)
✓ Created new Trade: TestSellerFLC - 01.06.25 (ID: Y)

📊 Starting ETL Process
   File: ..\Admin\DataUploads\seller_boarded_data_headers.csv
   Seller: Test Seller FLC (ID: X)
   Trade: TestSellerFLC - 01.06.25 (ID: Y)
   Mode: DRY RUN

📂 Reading file...
   ✓ Loaded 132 rows, 65 columns

🔍 Mapping columns...
   ✓ AI-generated column mapping
   Column Mapping:
      asset_hub → asset_hub
      current_balance → current_balance
      ... (more mappings)

🔄 Transforming and validating data...
   ✓ Valid records: 132

🔎 DRY RUN - Previewing first 5 records:
   Record 1:
      sellertape_id: 663283
      street_address: 45 KOONZ RD
      city: VOORHEESVILLE, state: NY
      current_balance: 451344.00
   ...

✓ DRY RUN COMPLETE - 132 records ready to import
```

### Step 3: Live Import (If Dry Run Looks Good)
```bash
# Remove --dry-run to actually import
python manage.py import_seller_data \
    --file ..\Admin\DataUploads\seller_boarded_data_headers.csv \
    --seller-name "Test Seller FLC" \
    --auto-create
```

**Expected Output:**
```
✓ Using existing Seller: Test Seller FLC (ID: X)
✓ Created new Trade: TestSellerFLC - 01.06.25 - 2 (ID: Y)

📊 Starting ETL Process
   ...

💾 Saving to database...
   Processing batch 1/2 (100 records)...
   Processing batch 2/2 (32 records)...
   ✓ Created 132 AssetIdHub records (1:1 with SellerRawData)
   ✓ Created: 132
   ✓ Skipped: 0

✅ ETL COMPLETE - Processed 132 records
```

### Step 4: Verify in Database
```bash
python manage.py shell
```

```python
from acq_module.models import SellerRawData, Seller, Trade

# Check seller
seller = Seller.objects.get(name="Test Seller FLC")
print(f"Seller: {seller.name}, ID: {seller.id}")

# Check trades
trades = seller.trades.all()
print(f"Number of trades: {trades.count()}")
for trade in trades:
    print(f"  - {trade.trade_name} (ID: {trade.id})")

# Check imported records
records = SellerRawData.objects.filter(seller=seller)
print(f"\nImported records: {records.count()}")

# View sample record
first = records.first()
print(f"\nSample Record:")
print(f"  Tape ID: {first.sellertape_id}")
print(f"  Address: {first.street_address}, {first.city}, {first.state}")
print(f"  Balance: ${first.current_balance:,.2f}")
print(f"  Asset Hub ID: {first.asset_hub_id}")

exit()
```

---

## Alternative Test: Simplest Auto-Create (No Seller Name)

The system will use the filename as the seller name:

```bash
# Seller name will be "seller boarded data headers"
python manage.py import_seller_data \
    --file ..\Admin\DataUploads\seller_boarded_data_headers.csv \
    --auto-create \
    --dry-run
```

---

## Test with Your Own File

```bash
# Place your file in Admin/DataUploads/
# Then run with auto-create

python manage.py import_seller_data \
    --file ..\Admin\DataUploads\YOUR_FILE.xlsx \
    --seller-name "Your Seller Name" \
    --auto-create \
    --dry-run
```

**What Happens:**
1. ✅ Creates new Seller record (or finds existing by name)
2. ✅ Creates new Trade record (auto-generated name with date)
3. ✅ Claude AI maps your columns to database fields
4. ✅ Validates and converts data types
5. ✅ Shows preview of first 5 records
6. ✅ Ready to import when you remove --dry-run

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
- Check your `.env` file has the key
- It's already there: `ANTHROPIC_API_KEY=sk-ant-api03-...`

### "No module named 'pandas'"
```bash
pip install pandas openpyxl xlrd
```

### "File not found"
- Use relative path from `projectalphav1` folder
- Or use absolute path: `C:\full\path\to\file.xlsx`

### Columns Not Mapping
- AI will attempt semantic matching
- View mapping in output
- Create custom mapping with `--save-mapping` and reuse

---

## Next Steps

1. ✅ Test with sample data (dry run)
2. ✅ Review AI column mapping
3. ✅ Run live import
4. ✅ Verify in database
5. 🎯 Import your real data files!

**System is ready to use!** 🚀
