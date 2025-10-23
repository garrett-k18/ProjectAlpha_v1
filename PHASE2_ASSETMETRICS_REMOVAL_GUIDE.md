# Phase 2: AssetMetrics Removal - Complete Guide

**Date:** 2025-10-23
**Status:** Ready to Execute
**Risk Level:** LOW - All pre-checks passed

---

## ✅ PHASE 1 RECAP - COMPLETED

### What Was Already Done:

1. **Admin Registrations Removed**
   - `am_module/admin.py` - AssetMetrics admin commented out
   - `core/admin.py` - SellerBoardedData references removed
   - All deprecated model admins disabled

2. **Model Exports Removed**
   - `am_module/models/__init__.py` - SellerBoardedData export removed

3. **Deprecation Warnings Added**
   - All 5 deprecated models have clear warning headers

4. **Production Status**
   - ✅ Deployed and working
   - ✅ Data showing up correctly
   - ✅ No errors: `python manage.py check` passes

---

## 🔍 PRE-PHASE 2 VERIFICATION - ASSETMETRICS

### Issue 1: Foreign Key References - ✅ CLEAR

**Scanned entire codebase for:**
- ForeignKey to AssetMetrics
- OneToOneField to AssetMetrics
- Any model dependencies

**Results:**
- ❌ No foreign keys found
- ✅ Only 1 comment mention in `core/models/transactions.py:449` (safe)
- ✅ No blocking dependencies

**Grep command used:**
```bash
grep -r "ForeignKey.*AssetMetrics" projectalphav1/ --include="*.py"
# Result: No matches found
```

### Issue 2: Migration Dependencies - ✅ SAFE

**Migration History:**
```
0001_initial.py
  └─ Creates AssetMetrics table

0003_remove_assetmetrics_asset_assetmetrics_asset_hub.py
  └─ Modifies AssetMetrics (changed FK from asset to asset_hub)

0004_ammetrics_ammetricschange_amnote_dil_fcsale_and_more.py
  └─ Depends on 0003 but doesn't touch AssetMetrics
  └─ Just creates AMMetrics (replacement model)
```

**Conclusion:** Migration chain is clean. Django will handle dependencies automatically.

---

## 📋 PHASE 2 EXECUTION STEPS

### Step 1: Create Git Safety Branch ⚠️ YOU DO THIS

```bash
cd c:\Users\garre\ProjectAlpha_v1
git status  # Make sure working tree is clean
git checkout -b phase2-remove-assetmetrics
git branch  # Verify you see * next to phase2-remove-assetmetrics
```

**Why?** Keeps `main` branch safe. Easy rollback if anything breaks.

---

### Step 2: Comment Out AssetMetrics Model

**File:** `projectalphav1/am_module/models/asset_metrics.py`

**Change this:**
```python
class AssetMetrics(models.Model): #deprecated delete in PRod
    """
    AssetMetrics tracks performance-related attributes for a single boarded asset.
    ... 60+ lines of code ...
    """
```

**To this:**
```python
# ============================================================
# MODEL REMOVED - Phase 2 Complete
# Table will be dropped by migration 0031
# ============================================================

# class AssetMetrics(models.Model): #deprecated delete in PRod
#     """
#     AssetMetrics tracks performance-related attributes for a single boarded asset.
#     ...entire class commented out...
#     """
```

**IMPORTANT:** Comment out the ENTIRE class including all:
- Fields
- Methods (time_held_days property)
- Meta class
- __str__ method

---

### Step 3: Generate Migration

```bash
cd projectalphav1
python manage.py makemigrations
```

**Expected Output:**
```
Migrations for 'am_module':
  am_module\migrations\0031_delete_assetmetrics.py
    - Delete model AssetMetrics
```

**If you see something different, STOP and review!**

---

### Step 4: Review Generated Migration File

**File will be:** `am_module/migrations/0031_delete_assetmetrics.py` (or similar number)

**Should look EXACTLY like this:**
```python
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('am_module', '0030_previous_migration_name'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AssetMetrics',
        ),
    ]
```

**✅ VERIFY:**
- Only ONE operation: `DeleteModel`
- No `RemoveField` operations
- No `AlterField` operations
- No `DeleteModel` for other models
- Correct dependency on your last migration

**❌ If you see ANYTHING else, STOP and investigate!**

---

### Step 5: Test Migration Locally

```bash
# Apply the migration to your local database
python manage.py migrate

# Expected output:
# Running migrations:
#   Applying am_module.0031_delete_assetmetrics... OK
```

**Check for errors:**
```bash
python manage.py check
# Should show: System check identified no issues (0 silenced).
```

**Test the app:**
```bash
python manage.py runserver
```

Then test:
- ✅ Admin panel loads: http://localhost:8000/admin
- ✅ API endpoints work
- ✅ No console errors

---

### Step 6: Verify Table is Deleted (Optional)

```bash
python manage.py dbshell
```

**In Postgres:**
```sql
\dt am_module_assetmetrics;
-- Should show: Did not find any relation named "am_module_assetmetrics"
```

**In SQLite:**
```sql
.tables
-- am_module_assetmetrics should NOT be in the list
```

Type `\q` or `.exit` to quit.

---

### Step 7: Commit Changes

```bash
git status  # Review what changed
git add .
git commit -m "Phase 2: Remove AssetMetrics model and database table

- Commented out AssetMetrics model class
- Generated migration 0031_delete_assetmetrics
- Tested locally - no issues
- Table dropped from database successfully"
```

---

### Step 8: Merge to Main and Deploy

```bash
# Switch back to main
git checkout main

# Merge the changes
git merge phase2-remove-assetmetrics

# Push to GitHub
git push origin main

# Deploy to production (Railway/your platform)
# Then in production shell:
python manage.py migrate
```

**Monitor production for errors!**

---

## 🚨 ROLLBACK PROCEDURES

### Scenario A: Migration File Looks Wrong (Before Step 5)

```bash
# Delete the migration file
rm projectalphav1/am_module/migrations/0031_delete_assetmetrics.py

# Uncomment the model class in asset_metrics.py
# (Just reverse Step 2)

# Try again or investigate why it generated wrong migration
```

---

### Scenario B: Local Migration Failed (During Step 5)

```bash
# Roll back the migration
python manage.py migrate am_module <previous_migration_number>

# Example:
python manage.py migrate am_module 0030

# Delete the migration file
rm projectalphav1/am_module/migrations/0031_delete_assetmetrics.py

# Uncomment the model class
```

---

### Scenario C: Local Tests Failed (After Step 5)

```bash
# Roll back migration
python manage.py migrate am_module <previous_migration_number>

# Delete migration file
rm projectalphav1/am_module/migrations/0031_delete_assetmetrics.py

# Uncomment model class

# Investigate what broke
python manage.py check
python manage.py runserver
# Check console/logs for errors
```

---

### Scenario D: Committed But Haven't Pushed

```bash
# Undo the commit
git reset --hard HEAD~1

# Or just make a new commit that reverses it
git revert HEAD
```

---

### Scenario E: Pushed But Not Deployed to Production

```bash
# Just don't run migrate in production yet
# Revert on GitHub if needed
git revert HEAD
git push
```

---

### Scenario F: Deployed to Production and BROKE ⚠️

```bash
# Option 1: Quick revert (recommended)
git revert HEAD
git push origin main
# In production:
python manage.py migrate  # Applies revert

# Option 2: Rollback migration in production
python manage.py migrate am_module <previous_migration_number>
# Then push code fix to uncomment model

# Option 3: Nuclear - restore from database backup
# (This is why we test locally first!)
```

---

### Scenario G: Nuclear - Delete Branch and Start Over

```bash
git checkout main
git branch -D phase2-remove-assetmetrics
# You're back to safety
# All changes on that branch are gone
# Main branch is untouched
```

---

## 📊 WHAT HAPPENS TECHNICALLY

### When You Run `makemigrations`:
1. Django detects AssetMetrics class is missing/commented
2. Compares to migration history (sees it was created in 0001)
3. Generates `DeleteModel` operation
4. Creates new migration file with dependency on last migration

### When You Run `migrate`:
1. Django checks migration history
2. Sees 0031 hasn't been applied yet
3. Runs SQL: `DROP TABLE am_module_assetmetrics;`
4. Records migration 0031 as applied in `django_migrations` table
5. Table is gone forever (unless you rollback)

### SQL Generated (Approximate):
```sql
-- Postgres
DROP TABLE IF EXISTS am_module_assetmetrics CASCADE;

-- SQLite
DROP TABLE IF EXISTS am_module_assetmetrics;
```

---

## 🔄 AFTER ASSETMETRICS: Remaining Models

Once AssetMetrics succeeds, repeat same process for:

1. **AMMetricsChange** (am_module)
   - Risk: LOW
   - No dependencies found
   - Quick win

2. **InternalValuation** (core)
   - Risk: MEDIUM
   - Check acq_module views first
   - May need view updates

3. **BrokerValues** (core)
   - Risk: MEDIUM
   - Check acq_module views first
   - May need view updates

4. **SellerBoardedData** (am_module)
   - Risk: HIGH
   - Lots of search_fields references
   - Most commented code
   - Save for last

**Recommendation:** Wait 1 day between each model removal to monitor production.

---

## ✅ PRE-FLIGHT CHECKLIST

Before starting Step 1:

- [ ] Phase 1 deployed and stable in production
- [ ] No errors in production logs
- [ ] Git working tree is clean (`git status`)
- [ ] You have database backup (optional since no data)
- [ ] You know how to rollback (read Scenario G above)
- [ ] You have time to monitor if issues arise
- [ ] You're on a non-critical day (not Friday night!)

---

## 📝 NOTES

- **No data loss risk:** You confirmed no data in any of these models
- **Migration is reversible:** Can rollback before deploying to prod
- **Branch keeps main safe:** Worst case, delete branch and restart
- **Test locally first:** Never run migrations in prod without local test
- **One at a time:** Don't do all 5 models at once

---

## 🎯 SUCCESS CRITERIA

Phase 2 for AssetMetrics is successful when:

- ✅ Migration generated cleanly (only DeleteModel operation)
- ✅ Local migration applied with no errors
- ✅ `python manage.py check` passes
- ✅ Admin panel loads
- ✅ API endpoints work
- ✅ Table verified deleted in dbshell
- ✅ Committed to branch
- ✅ Merged to main
- ✅ Deployed to production
- ✅ Production migrate runs successfully
- ✅ No errors in production for 24 hours

**Then proceed to AMMetricsChange!**

---

**CURRENT STATUS:** Waiting for user to create branch `phase2-remove-assetmetrics`

**NEXT STEP:** User runs: `git checkout -b phase2-remove-assetmetrics`
