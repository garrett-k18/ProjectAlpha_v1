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
print(f"DELETING EMPTY RECORDS - CREATED BETWEEN {start_of_today} AND {end_of_today}")
print("=" * 80)
print()

# Delete empty loan records
loan_deleted = SBDailyLoanData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id=''),
    models.Q(current_upb__isnull=True) | models.Q(current_upb='')
).delete()
print(f"✓ Deleted {loan_deleted[0]} empty SBDailyLoanData records")

# Delete empty foreclosure records
fc_deleted = SBDailyForeclosureData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).delete()
print(f"✓ Deleted {fc_deleted[0]} empty SBDailyForeclosureData records")

# Delete empty bankruptcy records
bk_deleted = SBDailyBankruptcyData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).delete()
print(f"✓ Deleted {bk_deleted[0]} empty SBDailyBankruptcyData records")

# Delete empty comment records
comment_deleted = SBDailyCommentData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).delete()
print(f"✓ Deleted {comment_deleted[0]} empty SBDailyCommentData records")

# Delete empty pay history records
pay_deleted = SBDailyPayHistoryData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_number__isnull=True) | models.Q(loan_number=''),
    models.Q(investor__isnull=True) | models.Q(investor='')
).delete()
print(f"✓ Deleted {pay_deleted[0]} empty SBDailyPayHistoryData records")

# Delete empty transaction records
trans_deleted = SBDailyTransactionData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(investor_id__isnull=True) | models.Q(investor_id='')
).delete()
print(f"✓ Deleted {trans_deleted[0]} empty SBDailyTransactionData records")

# Delete empty ARM records
arm_deleted = SBDailyArmData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).filter(
    models.Q(loan_id__isnull=True) | models.Q(loan_id=''),
    models.Q(loan_number__isnull=True) | models.Q(loan_number='')
).delete()
print(f"✓ Deleted {arm_deleted[0]} empty SBDailyArmData records")

# Delete cleaned ServicerLoanData records created today
servicer_deleted = ServicerLoanData.objects.filter(
    created_at__gte=start_of_today,
    created_at__lte=end_of_today
).delete()
print(f"✓ Deleted {servicer_deleted[0]} ServicerLoanData records")

print()
print("=" * 80)
print("CLEANUP COMPLETE!")
print("=" * 80)
total = (loan_deleted[0] + fc_deleted[0] + bk_deleted[0] + comment_deleted[0] + 
         pay_deleted[0] + trans_deleted[0] + arm_deleted[0] + servicer_deleted[0])
print(f"Total records deleted: {total}")
