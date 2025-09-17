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
from ..models.valuations import InternalValuation, BrokerValues


class InternalValuationSerializer(serializers.Serializer):
    """Serializer for the subset of InternalValuation fields the UI needs.
    Fields are optional on write to support PATCH semantics.
    """
    seller_raw_data = serializers.IntegerField(read_only=True)
    internal_uw_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_rehab_est_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    internal_uw_value_date = serializers.DateField(required=False, allow_null=True)
    # Read-only exposure of third-party values for display in UI (3rd Party BPO row)
    thirdparty_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    thirdparty_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    thirdparty_value_date = serializers.DateField(required=False, allow_null=True)
    # Read-only exposure of broker values for display in UI (Local Agent/Broker row)
    broker_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_rehab_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_value_date = serializers.DateField(required=False, allow_null=True)

    def to_representation(self, instance: Optional[InternalValuation]):
        if instance is None:
            return {
                "seller_raw_data": None,
                "internal_uw_asis_value": None,
                "internal_uw_arv_value": None,
                "internal_rehab_est_total": None,
                "internal_uw_value_date": None,
                # Keep response shape stable when missing
                "thirdparty_asis_value": None,
                "thirdparty_arv_value": None,
                "thirdparty_value_date": None,
                # Broker values shape
                "broker_asis_value": None,
                "broker_arv_value": None,
                "broker_rehab_est": None,
                "broker_value_date": None,
            }
        # Derive seller_raw_data id via hub (1:1): hub -> acq_raw
        raw = getattr(getattr(instance, 'asset_hub', None), 'acq_raw', None)
        return {
            "seller_raw_data": getattr(raw, 'id', None),
            # Treat stored zero as missing for display purposes so the UI shows blanks
            "internal_uw_asis_value": (
                str(instance.internal_uw_asis_value)
                if (instance.internal_uw_asis_value is not None and instance.internal_uw_asis_value != Decimal("0"))
                else None
            ),
            "internal_uw_arv_value": (
                str(instance.internal_uw_arv_value)
                if (instance.internal_uw_arv_value is not None and instance.internal_uw_arv_value != Decimal("0"))
                else None
            ),
            "internal_rehab_est_total": str(instance.internal_rehab_est_total) if instance.internal_rehab_est_total is not None else None,
            "internal_uw_value_date": instance.internal_uw_value_date.isoformat() if instance.internal_uw_value_date else None,
            # Third-party values surfaced for read in the valuation matrix (non-editable here)
            "thirdparty_asis_value": str(instance.thirdparty_asis_value) if getattr(instance, 'thirdparty_asis_value', None) is not None else None,
            "thirdparty_arv_value": str(instance.thirdparty_arv_value) if getattr(instance, 'thirdparty_arv_value', None) is not None else None,
            "thirdparty_value_date": instance.thirdparty_value_date.isoformat() if getattr(instance, 'thirdparty_value_date', None) else None,
            # Broker values fields included for convenience even when also using BrokerValues overlay
            "broker_asis_value": None,
            "broker_arv_value": None,
            "broker_rehab_est": None,
            "broker_value_date": None,
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

    # Resolve InternalValuation via hub 1:1
    try:
        iv = InternalValuation.objects.select_related('asset_hub').get(asset_hub=raw.asset_hub)
    except InternalValuation.DoesNotExist:
        iv = None

    if request.method == "GET":
        data = InternalValuationSerializer().to_representation(iv)
        # Ensure seller id is present even when iv is None (null payload)
        data["seller_raw_data"] = raw.id
        # Surface live BrokerValues as 3rd party values when available (via hub)
        try:
            broker = BrokerValues.objects.get(asset_hub=raw.asset_hub)
            data["thirdparty_asis_value"] = str(broker.broker_asis_value) if broker.broker_asis_value is not None else None
            data["thirdparty_arv_value"] = str(broker.broker_arv_value) if broker.broker_arv_value is not None else None
            data["thirdparty_value_date"] = broker.broker_value_date.isoformat() if broker.broker_value_date else None
            # Also return explicit broker_* keys for Local Agent/Broker row consumption
            data["broker_asis_value"] = str(broker.broker_asis_value) if broker.broker_asis_value is not None else None
            data["broker_arv_value"] = str(broker.broker_arv_value) if broker.broker_arv_value is not None else None
            data["broker_rehab_est"] = str(getattr(broker, 'broker_rehab_est', None)) if getattr(broker, 'broker_rehab_est', None) is not None else None
            data["broker_value_date"] = broker.broker_value_date.isoformat() if broker.broker_value_date else None
        except BrokerValues.DoesNotExist:
            # Leave whatever came from InternalValuation (possibly None)
            pass
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
        # Allow partial create: require at least one provided field; default date to today
        if (
            asis_val is None
            and arv_val is None
            and rehab_val is None
            and date_val is None
        ):
            return Response(
                {
                    "detail": "Provide at least one of internal_uw_asis_value, internal_uw_arv_value, internal_rehab_est_total, or internal_uw_value_date.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Satisfy non-null model constraints for internal As-Is/ARV by defaulting to 0.00 when omitted
        if asis_val is None:
            asis_val = Decimal("0.00")
        if arv_val is None:
            arv_val = Decimal("0.00")
        iv = InternalValuation.objects.create(
            asset_hub=raw.asset_hub,
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
