from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from etl.models import (
    SBDailyLoanData, 
    SBDailyForeclosureData, 
    SBDailyBankruptcyData,
    SBDailyCommentData,
    SBDailyPayHistoryData,
    SBDailyTransactionData,
    SBDailyArmData
)
from am_module.models import ServicerLoanData

# Define today's date range
today = timezone.now()
start_of_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
end_of_today = today

print("=" * 80)
print(f"RECORDS AFFECTED - CREATED BETWEEN {start_of_today} AND {end_of_today}")
print("=" * 80)
print()

# RAW STATEBRIDGE TABLES (etl.models)
print("RAW STATEBRIDGE TABLES (Empty Records Only)")
print("-" * 80)

# Check for records where all key business fields are blank/null
loan_empty = SBDailyLoanData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id=''),
    models.Q(current_upb__isnull=True) | models.Q(current_upb='')
).count()
print(f"  SBDailyLoanData (empty):           {loan_empty:>8} records")

fc_empty = SBDailyForeclosureData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).count()
print(f"  SBDailyForeclosureData (empty):    {fc_empty:>8} records")

bk_empty = SBDailyBankruptcyData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).count()
print(f"  SBDailyBankruptcyData (empty):     {bk_empty:>8} records")

comment_empty = SBDailyCommentData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).count()
print(f"  SBDailyCommentData (empty):        {comment_empty:>8} records")

pay_empty = SBDailyPayHistoryData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor__isnull=True) | models.Q(investor='')
).count()
print(f"  SBDailyPayHistoryData (empty):     {pay_empty:>8} records")

trans_empty = SBDailyTransactionData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).count()
print(f"  SBDailyTransactionData (empty):    {trans_empty:>8} records")

arm_empty = SBDailyArmData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(loan_number__isnull=True) | models.Q(loan_number='')
).count()
print(f"  SBDailyArmData (empty):            {arm_empty:>8} records")

raw_total = loan_empty + fc_empty + bk_empty + comment_empty + pay_empty + trans_empty + arm_empty
print(f"  {'SUBTOTAL (Raw Empty):':40} {raw_total:>8} records")

print()
print("CLEANED SERVICER TABLES (All Records)")
print("-" * 80)

servicer_all = ServicerLoanData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).count()
print(f"  ServicerLoanData (all):            {servicer_all:>8} records")

print()
print("=" * 80)
print(f"TOTAL RECORDS TO DELETE:             {raw_total + servicer_all:>8}")
print("=" * 80)
