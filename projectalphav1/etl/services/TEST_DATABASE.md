# ETL Testing Database Setup

## ⚠️ IMPORTANT: You've been using PRODUCTION database for tests!

Your `.env` file currently points to production:
```
DATABASE_URL=postgresql://...@ep-icy-haze-afnespkc-pooler...neon.tech/neondb
```

## ✅ Test Database Created

A separate **test branch** has been created in Neon:
- **Branch Name:** `etl-testing`
- **Branch ID:** `br-hidden-sound-af775rz8`
- **Status:** Empty copy of production schema (0 records)

## 🔧 How to Use Test Database

### Option 1: Update .env for testing (recommended)

1. **Backup your production `.env`:**
   ```bash
   copy .env .env.production
   ```

2. **Update `.env` with test database:**
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-restless-term-afx5ynub-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require
   GEMINI_API_KEY=AIzaSyAk9F3QBkXf9Q0LLGGhqXr0kRD6g4TpYDM
   ```

3. **Run your tests:**
   ```bash
   python projectalphav1/etl/services/test_multipass.py "C:\Users\garre\Documents\2004954286.Pdf"
   ```

4. **Restore production after testing:**
   ```bash
   copy .env.production .env
   ```

### Option 2: Create test scripts that use test DB

Modify test scripts to override DATABASE_URL:

```python
# At the top of your test script
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-restless-term-afx5ynub-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require'

# Then import Django
import django
django.setup()
```

## 📊 Check Test Data

After running tests, check what was written:

```sql
-- Count valuations
SELECT COUNT(*) FROM core.etl_valuation;

-- See recent extractions
SELECT * FROM core.etl_valuation ORDER BY created_at DESC LIMIT 5;
```

## 🗑️ Clean Up Test Data

```sql
-- Delete all test data
DELETE FROM core.etl_repair_item;
DELETE FROM core.etl_comparable;
DELETE FROM core.etl_valuation;
DELETE FROM core.etl_valuation_document;
```

## 🔄 Switch Back to Production

```bash
# Restore original .env
copy .env.production .env

# Or manually edit .env to use production:
DATABASE_URL=postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-icy-haze-afnespkc-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## 🚨 Current Status

- **Production DB:** ✅ Clean (0 test records)
- **Test DB:** ✅ Ready (branch: etl-testing)
- **Your .env:** ⚠️ Still pointing to PRODUCTION!

**NEXT STEP:** Switch `.env` to test database before running any more tests!

