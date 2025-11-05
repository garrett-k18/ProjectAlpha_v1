"""Quick script to verify GL entries in database"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectalphav1.settings')
django.setup()

from core.models.model_co_generalLedger import GeneralLedgerEntries

# Count total entries
total = GeneralLedgerEntries.objects.count()
print(f'Total GL Entries: {total}')

# Show sample entries
print(f'\nSample entries (first 5):')
for e in GeneralLedgerEntries.objects.all()[:5]:
    print(f'  {e.entry} - {e.company_name} - {e.account_number} - {e.account_name}')

# Check for duplicates
from django.db.models import Count
duplicates = GeneralLedgerEntries.objects.values('entry').annotate(count=Count('entry')).filter(count__gt=1)
print(f'\nDuplicate entries: {duplicates.count()}')



