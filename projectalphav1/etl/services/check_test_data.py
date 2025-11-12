"""
Check what data was written to the test database.
"""

import os

# Use test database
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_etXSFVQx7Nz3@ep-restless-term-afx5ynub-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require'

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectalphav1.settings")
django.setup()

from etl.models import ValuationETL, ComparablesETL, RepairItem

print("=" * 80)
print("🧪 TEST DATABASE CONTENTS")
print("=" * 80)

# Count records
val_count = ValuationETL.objects.count()
comp_count = ComparablesETL.objects.count()
repair_count = RepairItem.objects.count()

print(f"\n📊 Record Counts:")
print(f"   Valuations:  {val_count}")
print(f"   Comparables: {comp_count}")
print(f"   Repairs:     {repair_count}")

if val_count > 0:
    print(f"\n📋 Recent Valuations:")
    for val in ValuationETL.objects.order_by('-created_at')[:5]:
        print(f"   - {val.property_address or 'No address'} (Created: {val.created_at})")
        if val.comparables.exists():
            print(f"     → {val.comparables.count()} comparables")
        if val.repairs.exists():
            print(f"     → {val.repairs.count()} repairs")

print("\n" + "=" * 80)
print("✅ Check complete!")

