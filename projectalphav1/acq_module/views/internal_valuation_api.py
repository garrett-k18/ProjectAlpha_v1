"""
Internal Valuation API endpoints for acquisitions module.

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- Django get_object_or_404: https://docs.djangoproject.com/en/5.0/topics/http/shortcuts/

This module exposes a GET and PATCH/PUT endpoint to retrieve or update the
InternalValuation (internal underwriting values) for a given SellerRawData id.

URL shape: /api/acq/valuations/internal/<seller_id>/

Behavior:
- GET: returns the internal underwriting values if present, or an object with nulls
  if the InternalValuation row does not yet exist.
- PATCH/PUT: upserts the InternalValuation row. If it does not exist, it will be
  created using provided fields. Because the model has additional required fields
  for third-party values, we initialize those to 0 with today's date on creation.
  This lets the UI start capturing internal values without blocking on third-party.

Security:
- AllowAny for now (per project setup and user preference during development).
  Revisit and tighten permissions before production.
"""
from decimal import Decimal, InvalidOperation
from typing import Optional

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers

from ..models.seller import SellerRawData
from ..models.valuations import InternalValuation


class InternalValuationSerializer(serializers.Serializer):
    """Serializer for the subset of InternalValuation fields the UI needs.
    Fields are optional on write to support PATCH semantics.
    """
    seller_raw_data = serializers.IntegerField(read_only=True)
    internal_uw_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_value_date = serializers.DateField(required=False, allow_null=True)

    def to_representation(self, instance: Optional[InternalValuation]):
        if instance is None:
            return {
                "seller_raw_data": None,
                "internal_uw_asis_value": None,
                "internal_uw_arv_value": None,
                "internal_rehab_est_total": None,
                "internal_uw_value_date": None,
            }
        return {
            "seller_raw_data": instance.seller_raw_data_id,
            "internal_uw_asis_value": str(instance.internal_uw_asis_value) if instance.internal_uw_asis_value is not None else None,
            "internal_uw_arv_value": str(instance.internal_uw_arv_value) if instance.internal_uw_arv_value is not None else None,
            "internal_rehab_est_total": str(instance.internal_rehab_est_total) if instance.internal_rehab_est_total is not None else None,
            "internal_uw_value_date": instance.internal_uw_value_date.isoformat() if instance.internal_uw_value_date else None,
        }


@api_view(["GET", "PATCH", "PUT"])
@permission_classes([AllowAny])
def internal_valuation_detail(request, seller_id: int):
    """Retrieve or update InternalValuation by SellerRawData id.

    - GET  -> returns current values (or nulls if row doesn't exist)
    - PATCH/PUT -> updates existing row or creates a new one if missing

    On create, we must also set third-party fields required by the model;
    we default them to 0 and today's date.
    """
    raw = get_object_or_404(SellerRawData, pk=seller_id)

    try:
        iv = InternalValuation.objects.get(seller_raw_data=raw)
    except InternalValuation.DoesNotExist:
        iv = None

    if request.method == "GET":
        data = InternalValuationSerializer().to_representation(iv)
        # Ensure seller id is present even when iv is None (null payload)
        data["seller_raw_data"] = raw.id
        return Response(data, status=status.HTTP_200_OK)

    # Handle PATCH/PUT
    # Accept partial fields; coerce to Decimal when provided
    payload = request.data or {}

    def parse_decimal(value) -> Optional[Decimal]:
        if value in (None, "", "null"):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            raise serializers.ValidationError("Invalid decimal value")

    asis_in = payload.get("internal_uw_asis_value", None)
    arv_in = payload.get("internal_uw_arv_value", None)
    rehab_in = payload.get("internal_rehab_est_total", None)
    date_in = payload.get("internal_uw_value_date", None)

    # Validate decimals if provided
    if asis_in is not None:
        asis_val = parse_decimal(asis_in)
    else:
        asis_val = None

    if arv_in is not None:
        arv_val = parse_decimal(arv_in)
    else:
        arv_val = None

    if rehab_in is not None:
        rehab_val = parse_decimal(rehab_in)
    else:
        rehab_val = None

    # Coerce/validate date
    if date_in is None or date_in == "":
        date_val = None
    else:
        try:
            # serializers.DateField().to_internal_value for robust parsing
            date_val = serializers.DateField().to_internal_value(date_in)
        except serializers.ValidationError as e:
            return Response({"internal_uw_value_date": e.detail}, status=status.HTTP_400_BAD_REQUEST)

    # Create if missing
    if iv is None:
        # Both as-is and arv are required to create a new row, and date defaults to today
        if asis_val is None or arv_val is None:
            return Response({"detail": "internal_uw_asis_value and internal_uw_arv_value are required to create."}, status=status.HTTP_400_BAD_REQUEST)
        iv = InternalValuation.objects.create(
            seller_raw_data=raw,
            internal_uw_asis_value=asis_val,
            internal_uw_arv_value=arv_val,
            internal_rehab_est_total=rehab_val,
            internal_uw_value_date=date_val or timezone.now().date(),
            # Third-party required fields: initialize to zero/today; UI will manage later via a dedicated screen
            thirdparty_asis_value=Decimal("0.00"),
            thirdparty_arv_value=Decimal("0.00"),
            thirdparty_value_date=timezone.now().date(),
        )
    else:
        # Update only provided fields (PATCH semantics also for PUT here)
        if asis_val is not None:
            iv.internal_uw_asis_value = asis_val
        if arv_val is not None:
            iv.internal_uw_arv_value = arv_val
        if rehab_val is not None:
            iv.internal_rehab_est_total = rehab_val
        if date_val is not None:
            iv.internal_uw_value_date = date_val
        iv.save()

    data = InternalValuationSerializer().to_representation(iv)
    return Response(data, status=status.HTTP_200_OK)
