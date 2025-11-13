# ETL Field Audit Report

## Issues Found

### 1. **ComparablesETL Admin - Invalid Field Reference**
- **File:** `projectalphav1/etl/admin.py` (line 424)
- **Issue:** References `garage_spaces` which does NOT exist in ComparablesETL model
- **Fix:** Remove `garage_spaces` from admin (ValuationETL has it, but ComparablesETL only has `garage` and `parking_spaces`)

### 2. **ComparablesETL - Field in Model but Skipped in Extraction**
- **File:** `projectalphav1/etl/models/model_etl_valueImports.py` (line 299)
- **Issue:** `adjustments_description` exists in model BUT is in `_SKIP_FIELD_NAMES` (extractor line 109)
- **Decision Needed:** 
  - Remove from model (if we don't need it), OR
  - Remove from skip list (if we want Gemini to extract it)
- **Recommendation:** REMOVE from model since we already have `general_comments` and adjustments are simplified

## Fields That Are Correctly Set Up

### ValuationETL (96 total fields after exclusions)
All fields in model match extraction + admin ✅

### ComparablesETL (31 total fields after exclusions)
Almost all match - just the 2 issues above

### RepairItem (5 total fields after exclusions)
All fields match ✅

## Summary
- **Admin Issue:** 1 field reference to non-existent field
- **Model/Skip Mismatch:** 1 field exists in model but won't be extracted

