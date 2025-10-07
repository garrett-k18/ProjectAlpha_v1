import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectalphav1.settings')
django.setup()

from acq_module.models.seller import SellerRawData

# Check specific records
records = SellerRawData.objects.filter(
    sellertape_id__in=['9160091926', '9160091918', '9160091914', '9160091912', '9160091910']
).values('sellertape_id', 'property_type')

print("\n=== Property Type Check ===")
for r in records:
    prop_type = r['property_type']
    display = f"'{prop_type}'" if prop_type else "NULL/BLANK"
    print(f"ID: {r['sellertape_id']}, Property Type: {display}")

# Check all Phenoix records
print("\n=== All Phenoix Property Types ===")
all_records = SellerRawData.objects.filter(seller__name='Phenoix Capital').values('property_type').distinct()
for r in all_records:
    prop_type = r['property_type']
    display = f"'{prop_type}'" if prop_type else "NULL/BLANK"
    count = SellerRawData.objects.filter(seller__name='Phenoix Capital', property_type=prop_type).count()
    print(f"Property Type: {display} - Count: {count}")
