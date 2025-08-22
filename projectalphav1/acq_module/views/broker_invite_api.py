"""
Broker Invite API endpoints for tokenized, loginless access by external brokers.

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
- Django timezone utilities: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/

Security notes:
- validate/submit endpoints are public (AllowAny) because access control is via the token.
- create endpoint is also AllowAny for now to match existing project style; tighten to IsAuthenticated in prod.
"""
from decimal import Decimal, InvalidOperation
from typing import Optional
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from django.db.models import Q

from ..models import SellerRawData, BrokerValues, Brokercrm
from user_admin.models import BrokerTokenAuth


class BrokerValuesInputSerializer(serializers.Serializer):
    broker_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_value_date = serializers.DateField(required=False, allow_null=True)
    broker_rehab_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


def _parse_decimal(value) -> Optional[Decimal]:
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise serializers.ValidationError("Invalid decimal value")


@api_view(["POST"])  # TODO: tighten to IsAuthenticated before production
@permission_classes([AllowAny])
def create_broker_invite(request):
    """Create a new token invite for a SellerRawData id (via BrokerTokenAuth).

    Body fields:
    - seller_raw_data: int (required)
    - expires_in_hours: int (optional, default 72)
    - expires_at: ISO date-time string (optional; overrides expires_in_hours)
    - broker_id: int (optional, FK to acq_module.Brokercrm)
    - single_use: bool (default True)
    - notes: string (optional)
    """
    payload = request.data or {}
    srd_id = payload.get("seller_raw_data")
    if not srd_id:
        return Response({"detail": "seller_raw_data is required"}, status=status.HTTP_400_BAD_REQUEST)

    srd = get_object_or_404(SellerRawData, pk=srd_id)

    # Expiration handling
    expires_at_in = payload.get("expires_at")
    if expires_at_in:
        try:
            expires_at = serializers.DateTimeField().to_internal_value(expires_at_in)
        except serializers.ValidationError as e:
            return Response({"expires_at": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    else:
        hours = payload.get("expires_in_hours", 72)
        try:
            hours = int(hours)
        except (TypeError, ValueError):
            return Response({"expires_in_hours": "Must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        expires_at = timezone.now() + timedelta(hours=hours)

    single_use = bool(payload.get("single_use", True))
    notes = payload.get("notes")
    broker_id = payload.get("broker_id")

    # Generate a unique token
    token = BrokerTokenAuth.generate_token()
    while BrokerTokenAuth.objects.filter(token=token).exists():  # extremely unlikely
        token = BrokerTokenAuth.generate_token()

    invite = BrokerTokenAuth.objects.create(
        seller_raw_data=srd,
        token=token,
        expires_at=expires_at,
        single_use=single_use,
        notes=notes,
        broker_id=broker_id if broker_id else None,
    )

    return Response(
        {
            "seller_raw_data": invite.seller_raw_data_id,
            "token": invite.token,
            "expires_at": invite.expires_at.isoformat(),
            "single_use": invite.single_use,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def validate_broker_invite(request, token: str):
    """Validate a broker invite token and return minimal context.

    Returns:
    - valid: bool
    - reason: optional string if invalid
    - expires_at: ISO string
    - seller_raw_data: int
    """
    try:
        invite = BrokerTokenAuth.objects.get(token=token)
    except BrokerTokenAuth.DoesNotExist:
        return Response({"valid": False, "reason": "not_found"}, status=status.HTTP_404_NOT_FOUND)

    if invite.is_expired:
        return Response(
            {
                "valid": False,
                "reason": "expired",
                "expires_at": invite.expires_at.isoformat(),
                "seller_raw_data": invite.seller_raw_data_id,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if invite.single_use and invite.is_used:
        return Response(
            {
                "valid": False,
                "reason": "used",
                "expires_at": invite.expires_at.isoformat(),
                "seller_raw_data": invite.seller_raw_data_id,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "valid": True,
            "expires_at": invite.expires_at.isoformat(),
            "seller_raw_data": invite.seller_raw_data_id,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def submit_broker_values_with_token(request, token: str):
    """Submit broker values using a valid invite token.

    Behavior:
    - Validates token (exists, not expired, not used if single-use)
    - Upserts BrokerValues for the linked SellerRawData
    - If invite.single_use, marks used_at on first successful submission
    """
    try:
        invite = BrokerTokenAuth.objects.get(token=token)
    except BrokerTokenAuth.DoesNotExist:
        return Response({"detail": "invalid_token"}, status=status.HTTP_404_NOT_FOUND)

    if not invite.is_valid():
        reason = "expired" if invite.is_expired else "used"
        return Response({"detail": f"token_{reason}"}, status=status.HTTP_400_BAD_REQUEST)

    srd = invite.seller_raw_data

    # Validate input
    serializer = BrokerValuesInputSerializer(data=request.data or {})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Upsert BrokerValues
    try:
        bv = BrokerValues.objects.get(seller_raw_data=srd)
    except BrokerValues.DoesNotExist:
        bv = BrokerValues(seller_raw_data=srd)

    if "broker_asis_value" in data:
        bv.broker_asis_value = data["broker_asis_value"]
    if "broker_arv_value" in data:
        bv.broker_arv_value = data["broker_arv_value"]
    if "broker_rehab_est" in data:
        bv.broker_rehab_est = data["broker_rehab_est"]
    if "broker_value_date" in data:
        bv.broker_value_date = data["broker_value_date"]
    if "broker_notes" in data:
        bv.broker_notes = data["broker_notes"]

    bv.save()

    # Mark token as used when single_use
    if invite.single_use and not invite.is_used:
        invite.used_at = timezone.now()
        invite.save(update_fields=["used_at"])

    return Response(
        {
            "seller_raw_data": srd.id,
            "broker_asis_value": str(bv.broker_asis_value) if bv.broker_asis_value is not None else None,
            "broker_arv_value": str(bv.broker_arv_value) if bv.broker_arv_value is not None else None,
            "broker_rehab_est": str(bv.broker_rehab_est) if getattr(bv, 'broker_rehab_est', None) is not None else None,
            "broker_value_date": bv.broker_value_date.isoformat() if bv.broker_value_date else None,
            "broker_notes": bv.broker_notes,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])  # Exposed for internal UI use; keep auth open for now
@permission_classes([AllowAny])
def list_brokers_by_state_batch(request):
    """Return unique brokers keyed by state for the provided state codes.

    Query Params:
    - states: comma-separated list of state codes (e.g., "CA,TX,FL").

    Notes:
    - We deduplicate brokers primarily by email when present; otherwise by
      (broker_name, broker_firm). This treats multiple invites of the same
      person as one option in the UI.
    - This endpoint is intended to power an AG Grid select editor; no
      preselection is performed server-side.

    Response shape:
    {
      "results": {
        "CA": [
          {"broker_name": "Jane Doe", "broker_email": "jane@example.com", "broker_firm": "Acme Realty"},
          ...
        ],
        "TX": [...]
      }
    }
    """
    states_param = request.query_params.get("states", "")
    # Normalize requested states to uppercase without whitespace
    states = [s.strip().upper() for s in states_param.split(",") if s.strip()]
    if not states:
        return Response({"detail": "states is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch all Brokercrm rows that have one of the requested states (case-insensitive).
    # Use Q objects to ensure case-insensitive matching per element.
    q = Q()
    for s in states:
        q |= Q(broker_state__iexact=s)
    qs = Brokercrm.objects.filter(q)

    # Build a map of state -> unique broker entries
    results = {state: [] for state in states}
    # Track seen keys per state to de-duplicate
    seen_keys = {state: set() for state in states}

    for b in qs.only("broker_state", "broker_name", "broker_email", "broker_firm", "broker_city"):
        state = (b.broker_state or "").upper()
        if state not in results:
            # If a Brokercrm row has a state not requested, skip it
            continue
        # Compose a stable deduplication key
        key = (b.broker_email or "").lower().strip() or f"{(b.broker_name or '').strip()}|{(b.broker_firm or '').strip()}"
        if key in seen_keys[state]:
            continue
        seen_keys[state].add(key)
        results[state].append(
            {
                "broker_name": b.broker_name,
                "broker_email": b.broker_email,
                "broker_firm": b.broker_firm,
                "broker_city": b.broker_city,
            }
        )

    return Response({"results": results}, status=status.HTTP_200_OK)
