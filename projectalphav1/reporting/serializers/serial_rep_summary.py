"""
Serializer: Summary KPIs

WHAT: Field definitions for reporting dashboard summary metrics (top bar)
WHY: Define API contract for KPI endpoint
WHERE: Imported by view_rep_summary.py
HOW: Define exactly 4 key metrics for header display

FILE NAMING: serial_rep_summary.py
- serial_ = Serializers folder
- _rep_ = Reporting module
- summary = Summary KPIs

Docs reviewed:
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
"""

from rest_framework import serializers


class SummaryKPISerializer(serializers.Serializer):
    """
    WHAT: Field definitions for summary KPI metrics
    WHY: Define top bar metrics displayed above all reports
    WHERE: Used by report_summary endpoint
    
    FIELDS: The 4 key portfolio metrics
    - total_upb: Total unpaid principal balance
    - asset_count: Total number of assets
    - avg_ltv: Average loan-to-value ratio
    - delinquency_rate: Percentage of delinquent assets
    """
    # WHAT: Total unpaid principal balance across all filtered assets
    # WHY: Primary portfolio size metric
    # HOW: Sum of all current_balance values
    total_upb = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Total unpaid principal balance"
    )
    
    # WHAT: Total count of assets in filtered dataset
    # WHY: Portfolio size by count
    # HOW: COUNT(*) on filtered queryset
    asset_count = serializers.IntegerField(
        help_text="Total number of assets"
    )
    
    # WHAT: Average loan-to-value ratio
    # WHY: Risk metric - higher LTV = higher risk
    # HOW: AVG(current_balance / as_is_value * 100)
    avg_ltv = serializers.FloatField(
        help_text="Average LTV percentage"
    )
    
    # WHAT: Delinquency rate (percentage)
    # WHY: Portfolio quality metric
    # HOW: (COUNT where months_dlq > 0) / total_count * 100
    delinquency_rate = serializers.FloatField(
        help_text="Percentage of delinquent assets"
    )
    
    # ========================================================================
    # 🎯 ADD ADDITIONAL KPI FIELDS HERE IF NEEDED
    # ========================================================================
    # 
    # EXAMPLES:
    # avg_interest_rate = serializers.FloatField(required=False)
    # total_debt = serializers.DecimalField(max_digits=15, decimal_places=2)
    # fc_rate = serializers.FloatField(required=False)  # % in foreclosure
    # occupied_rate = serializers.FloatField(required=False)  # % occupied
    # ========================================================================

