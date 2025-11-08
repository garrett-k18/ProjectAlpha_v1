"""
[NOTE] Broker values are now stored in unified Valuation (source='broker').
This module was updated to use `core.models.valuations.Valuation` instead of
the legacy `BrokerValues` model. Payload shapes remain the same for backward
compatibility with the frontend.
Public (token-based) broker invite API endpoints.

Responsibilities:
- Public invite lifecycle (single-use token links)
- By-state batch broker listing for UI population
- Token-bound access; endpoints are AllowAny but guarded by token validation
- Separate from internal staff endpoints (`internal.py`) and portal batch flows (`portal.py`)

Plain-language overview:
- These endpoints power the external broker workflow via loginless token links.
- Tokens are created by internal users and sent to brokers; the broker uses the
  tokenized link to view/submit data for a single asset (SellerRawData).
- SECURITY: Access is controlled by the token; therefore these endpoints are
  AllowAny. Ensure tokens are sufficiently random and time-bounded.
- Shared, read-only data needs for internal UI should live in
  acq_module.services.brokers to avoid duplication.

Endpoints provided here:
- POST /api/acq/broker-invites/                     -> create_broker_invite
- GET  /api/acq/broker-invites/<token>/             -> validate_broker_invite
- POST /api/acq/broker-invites/<token>/submit/      -> submit_broker_values_with_token
- GET  /api/acq/broker-invites/by-state-batch/      -> list_brokers_by_state_batch

Docs reviewed:
- DRF API Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
- Django timezone utilities: https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/
"""
from decimal import Decimal, InvalidOperation
from typing import Optional
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

from ...models.model_acq_seller import SellerRawData
from core.models.valuations import Valuation
from core.models.attachments import Photo, Document
from core.models.model_co_crm import MasterCRM
from user_admin.models import BrokerTokenAuth


class BrokerValuesInputSerializer(serializers.Serializer):
    """Serializer for values a broker can submit via a tokenized form.
    
    WHAT: Accept broker valuation inputs including grade and detailed rehab breakdown
    WHY: Allow brokers to provide complete valuation data with itemized repair estimates
    HOW: Validate and serialize all broker-provided fields including trade categories
    """
    broker_asis_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_arv_value = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_value_date = serializers.DateField(required=False, allow_null=True)
    broker_rehab_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)  # WHAT: Broker quality grade (A+, A, B, C, D, F)
    broker_links = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    # WHAT: Detailed rehab breakdown by trade category (grade + cost estimate)
    # WHY: Allow brokers to provide itemized repair estimates with condition grades
    # HOW: Separate fields for each major trade (roof, kitchen, bath, etc.)
    broker_roof_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_roof_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_kitchen_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_kitchen_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_bath_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_bath_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_flooring_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_flooring_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_windows_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_windows_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_appliances_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_appliances_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_plumbing_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_plumbing_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_electrical_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_electrical_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    broker_landscaping_grade = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    broker_landscaping_est = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)


def _parse_decimal(value) -> Optional[Decimal]:
    """Utility to parse a decimal-like input safely."""
    if value in (None, "", "null"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise serializers.ValidationError("Invalid decimal value")


@api_view(["POST"])  # TODO: tighten to IsAuthenticated before production if required
@permission_classes([AllowAny])
def create_broker_invite(request):
    """Create a new token invite for an AssetIdHub (via BrokerTokenAuth).

    WHAT: Hub-first architecture - create invites for asset hub IDs
    WHY: All joins happen through AssetIdHub intentionally
    HOW: Accept asset_hub_id or seller_raw_data (backward compat - same values)

    Body fields:
    - asset_hub_id: int (preferred, hub-first)
    - seller_raw_data: int (backward compat - same as asset_hub_id)
    - expires_in_hours: int (optional, default 360 [15 days])
    - expires_at: ISO date-time string (optional; overrides expires_in_hours)
    - broker_id: int (optional, FK to core.MasterCRM)
    - single_use: bool (default True)
    - notes: string (optional)
    """
    payload = request.data or {}
    # WHAT: Accept either asset_hub_id (preferred) or seller_raw_data (backward compat)
    # WHY: Hub-first architecture but support existing API clients
    # HOW: Same values since SellerRawData uses hub as PK
    hub_id = payload.get("asset_hub_id") or payload.get("seller_raw_data")
    if not hub_id:
        return Response({"detail": "asset_hub_id or seller_raw_data is required"}, status=status.HTTP_400_BAD_REQUEST)

    from core.models.asset_id_hub import AssetIdHub
    hub = get_object_or_404(AssetIdHub, pk=hub_id)

    # Expiration handling
    expires_at_in = payload.get("expires_at")
    if expires_at_in:
        try:
            expires_at = serializers.DateTimeField().to_internal_value(expires_at_in)
        except serializers.ValidationError as e:
            return Response({"expires_at": e.detail}, status=status.HTTP_400_BAD_REQUEST)
    else:
        hours = payload.get("expires_in_hours", 360)  # default 15 days
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
        asset_hub=hub,
        token=token,
        expires_at=expires_at,
        single_use=single_use,
        notes=notes,
        broker_id=broker_id if broker_id else None,
    )

    return Response(
        {
            "asset_hub_id": invite.asset_hub_id,
            "seller_raw_data": invite.asset_hub_id,  # Backward compat (same value)
            "token": invite.token,
            "expires_at": invite.expires_at.isoformat(),
            "single_use": invite.single_use,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])  # Public validation for loginless flow
@permission_classes([AllowAny])
def validate_broker_invite(request, token: str):
    """Validate a broker invite token and return minimal context.

    WHAT: Hub-first architecture - validate token and return hub context
    WHY: All joins through AssetIdHub intentionally
    HOW: Access via asset_hub FK directly

    Returns:
    - valid: bool
    - reason: optional string if invalid
    - expires_at: ISO string
    - asset_hub_id: int
    - seller_raw_data: int (backward compat - same as asset_hub_id)
    """
    try:
        invite = BrokerTokenAuth.objects.get(token=token)
    except BrokerTokenAuth.DoesNotExist:
        return Response({"valid": False, "reason": "not_found"}, status=status.HTTP_404_NOT_FOUND)

    # WHAT: Load any previously saved broker Valuation for prefill visibility even when invalid
    # WHY: UX - show previously submitted values even if token expired
    # HOW: Hub-first query - filter by asset_hub FK directly
    bv = (
        Valuation.objects
        .filter(asset_hub=invite.asset_hub, source='broker')
        .order_by('-value_date', '-created_at')
        .first()
    )
    values = None
    if bv:
        # WHAT: Serialize grade FK to code string
        # WHY: grade is a ForeignKey to ValuationGradeReference, need to extract code
        # HOW: Access grade.code if grade FK is populated
        grade_obj = getattr(bv, "grade", None)
        grade_code = getattr(grade_obj, "code", None) if grade_obj else None
        
        values = {
            "broker_asis_value": str(bv.broker_asis_value) if getattr(bv, "broker_asis_value", None) is not None else None,
            "broker_arv_value": str(bv.broker_arv_value) if getattr(bv, "broker_arv_value", None) is not None else None,
            "broker_rehab_est": str(getattr(bv, "broker_rehab_est", None)) if getattr(bv, "broker_rehab_est", None) is not None else None,
            "broker_value_date": bv.broker_value_date.isoformat() if getattr(bv, "broker_value_date", None) else None,
            "broker_notes": getattr(bv, "broker_notes", None),
            "broker_grade": grade_code,  # WHAT: Grade code (A+, A, B, C, D, F) as string
            "broker_links": getattr(bv, "broker_links", None),
            # WHAT: Include detailed rehab breakdown fields for prefill
            # WHY: Show existing data when broker reopens modal
            "broker_roof_grade": getattr(bv, "broker_roof_grade", None),
            "broker_roof_est": getattr(bv, "broker_roof_est", None),
            "broker_kitchen_grade": getattr(bv, "broker_kitchen_grade", None),
            "broker_kitchen_est": getattr(bv, "broker_kitchen_est", None),
            "broker_bath_grade": getattr(bv, "broker_bath_grade", None),
            "broker_bath_est": getattr(bv, "broker_bath_est", None),
            "broker_flooring_grade": getattr(bv, "broker_flooring_grade", None),
            "broker_flooring_est": getattr(bv, "broker_flooring_est", None),
            "broker_windows_grade": getattr(bv, "broker_windows_grade", None),
            "broker_windows_est": getattr(bv, "broker_windows_est", None),
            "broker_appliances_grade": getattr(bv, "broker_appliances_grade", None),
            "broker_appliances_est": getattr(bv, "broker_appliances_est", None),
            "broker_plumbing_grade": getattr(bv, "broker_plumbing_grade", None),
            "broker_plumbing_est": getattr(bv, "broker_plumbing_est", None),
            "broker_electrical_grade": getattr(bv, "broker_electrical_grade", None),
            "broker_electrical_est": getattr(bv, "broker_electrical_est", None),
            "broker_landscaping_grade": getattr(bv, "broker_landscaping_grade", None),
            "broker_landscaping_est": getattr(bv, "broker_landscaping_est", None),
        }

    if invite.is_expired:
        return Response(
            {
                "valid": False,
                "reason": "expired",
                "expires_at": invite.expires_at.isoformat(),
                "asset_hub_id": invite.asset_hub_id,
                "seller_raw_data": invite.asset_hub_id,  # Backward compat
                "values": values,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if invite.single_use and invite.is_used:
        return Response(
            {
                "valid": False,
                "reason": "used",
                "expires_at": invite.expires_at.isoformat(),
                "asset_hub_id": invite.asset_hub_id,
                "seller_raw_data": invite.asset_hub_id,  # Backward compat
                "values": values,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "valid": True,
            "expires_at": invite.expires_at.isoformat(),
            "asset_hub_id": invite.asset_hub_id,
            "seller_raw_data": invite.asset_hub_id,  # Backward compat
            "values": values,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])  # Public submission endpoint
@permission_classes([AllowAny])
def submit_broker_values_with_token(request, token: str):
    """Submit broker values using a valid invite token.

    WHAT: Hub-first architecture - upsert Valuation via asset_hub
    WHY: All joins through AssetIdHub intentionally
    HOW: Access asset_hub FK directly instead of through seller_raw_data

    Behavior:
    - Validates token (exists, not expired, not used if single-use)
    - Upserts Valuation for the linked AssetIdHub
    - If invite.single_use, marks used_at on first successful submission
    """
    try:
        invite = BrokerTokenAuth.objects.get(token=token)
    except BrokerTokenAuth.DoesNotExist:
        return Response({"detail": "invalid_token"}, status=status.HTTP_404_NOT_FOUND)

    # Portal requirement: tokens should remain usable until expiration.
    # Only block on expiration; ignore prior submissions/used flag.
    if invite.is_expired:
        return Response({"detail": "token_expired"}, status=status.HTTP_400_BAD_REQUEST)

    # WHAT: Access asset hub directly (hub-first)
    # WHY: All domain data accessed through hub
    # HOW: invite.asset_hub FK (no need to go through seller_raw_data)
    hub = invite.asset_hub

    # Validate input
    serializer = BrokerValuesInputSerializer(data=request.data or {})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # WHAT: Upsert Valuation (source='broker') via hub
    # WHY: One row per date per hub via unique constraint
    # HOW: update_or_create on (asset_hub, source, value_date)
    lookup = {
        'asset_hub': hub,
        'source': 'broker',
        'value_date': data.get('broker_value_date'),
    }
    
    # WHAT: Lookup ValuationGradeReference by code if provided
    # WHY: grade is a ForeignKey, need to resolve code string to FK instance
    # HOW: Query ValuationGradeReference by code, set to None if not found
    grade_fk = None
    grade_code = data.get('broker_grade')
    if grade_code:
        from core.models.valuations import ValuationGradeReference
        try:
            grade_fk = ValuationGradeReference.objects.get(code=grade_code)
        except ValuationGradeReference.DoesNotExist:
            pass  # Leave as None if invalid code
    
    defaults = {
        'asis_value': data.get('broker_asis_value'),
        'arv_value': data.get('broker_arv_value'),
        'rehab_est_total': data.get('broker_rehab_est'),
        'notes': data.get('broker_notes'),
        'grade': grade_fk,  # WHAT: Store grade FK (resolved from code)
        'links': data.get('broker_links'),
        # WHAT: Detailed rehab breakdown by trade category
        # WHY: Store itemized repair estimates with condition grades from broker inspection
        # HOW: Store each trade's grade and cost estimate in corresponding Valuation fields
        'broker_roof_grade': data.get('broker_roof_grade'),
        'broker_roof_est': data.get('broker_roof_est'),
        'broker_kitchen_grade': data.get('broker_kitchen_grade'),
        'broker_kitchen_est': data.get('broker_kitchen_est'),
        'broker_bath_grade': data.get('broker_bath_grade'),
        'broker_bath_est': data.get('broker_bath_est'),
        'broker_flooring_grade': data.get('broker_flooring_grade'),
        'broker_flooring_est': data.get('broker_flooring_est'),
        'broker_windows_grade': data.get('broker_windows_grade'),
        'broker_windows_est': data.get('broker_windows_est'),
        'broker_appliances_grade': data.get('broker_appliances_grade'),
        'broker_appliances_est': data.get('broker_appliances_est'),
        'broker_plumbing_grade': data.get('broker_plumbing_grade'),
        'broker_plumbing_est': data.get('broker_plumbing_est'),
        'broker_electrical_grade': data.get('broker_electrical_grade'),
        'broker_electrical_est': data.get('broker_electrical_est'),
        'broker_landscaping_grade': data.get('broker_landscaping_grade'),
        'broker_landscaping_est': data.get('broker_landscaping_est'),
    }
    # Null value_date would violate the unique constraint semantics; allow a None-date upsert by using created_at latest
    if lookup['value_date'] is None:
        # fallback to latest existing broker valuation for hub
        bv = (
            Valuation.objects
            .filter(asset_hub=hub, source='broker')
            .order_by('-value_date', '-created_at')
            .first()
        )
        if bv:
            # update existing latest
            for k, v in defaults.items():
                setattr(bv, k, v)
            bv.save()
        else:
            bv = Valuation.objects.create(asset_hub=hub, source='broker', **defaults)
    else:
        bv, _created = Valuation.objects.update_or_create(defaults=defaults, **lookup)

    # Mark token as used when single_use
    if invite.single_use and not invite.is_used:
        invite.used_at = timezone.now()
        invite.save(update_fields=["used_at"])

    # WHAT: Serialize grade FK to code string for response
    # WHY: Frontend expects string code, not model object
    # HOW: Access grade.code if grade FK is populated
    grade_obj = getattr(bv, "grade", None)
    grade_code_response = getattr(grade_obj, "code", None) if grade_obj else None
    
    return Response(
        {
            "asset_hub_id": hub.id,
            "seller_raw_data": hub.id,  # Backward compat (same value)
            # WHAT: Map Valuation model fields to broker-prefixed response keys
            # WHY: Valuation model uses asis_value, arv_value, etc. (not broker_ prefix)
            # HOW: getattr with correct model field names, return with broker_ prefix for frontend
            "broker_asis_value": str(getattr(bv, 'asis_value', None)) if getattr(bv, 'asis_value', None) is not None else None,
            "broker_arv_value": str(getattr(bv, 'arv_value', None)) if getattr(bv, 'arv_value', None) is not None else None,
            "broker_rehab_est": str(getattr(bv, 'rehab_est_total', None)) if getattr(bv, 'rehab_est_total', None) is not None else None,
            "broker_value_date": getattr(bv, 'value_date', None).isoformat() if getattr(bv, 'value_date', None) else None,
            "broker_notes": getattr(bv, 'notes', None),
            "broker_grade": grade_code_response,  # WHAT: Return grade code string (A+, A, B, etc.)
            "broker_links": getattr(bv, "links", None),
            # WHAT: Return detailed rehab breakdown fields
            # WHY: Frontend needs these to update UI after save
            # HOW: Include all grade and cost fields for each trade category
            "broker_roof_grade": getattr(bv, "broker_roof_grade", None),
            "broker_roof_est": getattr(bv, "broker_roof_est", None),
            "broker_kitchen_grade": getattr(bv, "broker_kitchen_grade", None),
            "broker_kitchen_est": getattr(bv, "broker_kitchen_est", None),
            "broker_bath_grade": getattr(bv, "broker_bath_grade", None),
            "broker_bath_est": getattr(bv, "broker_bath_est", None),
            "broker_flooring_grade": getattr(bv, "broker_flooring_grade", None),
            "broker_flooring_est": getattr(bv, "broker_flooring_est", None),
            "broker_windows_grade": getattr(bv, "broker_windows_grade", None),
            "broker_windows_est": getattr(bv, "broker_windows_est", None),
            "broker_appliances_grade": getattr(bv, "broker_appliances_grade", None),
            "broker_appliances_est": getattr(bv, "broker_appliances_est", None),
            "broker_plumbing_grade": getattr(bv, "broker_plumbing_grade", None),
            "broker_plumbing_est": getattr(bv, "broker_plumbing_est", None),
            "broker_electrical_grade": getattr(bv, "broker_electrical_grade", None),
            "broker_electrical_est": getattr(bv, "broker_electrical_est", None),
            "broker_landscaping_grade": getattr(bv, "broker_landscaping_grade", None),
            "broker_landscaping_est": getattr(bv, "broker_landscaping_est", None),
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])  # Exposed for internal UI use; open for now
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
    states = [s.strip().upper() for s in states_param.split(",") if s.strip()]
    if not states:
        return Response({"detail": "states is required"}, status=status.HTTP_400_BAD_REQUEST)

    q = Q()
    for s in states:
        q |= Q(broker_state__iexact=s)
    qs = Brokercrm.objects.filter(q)

    results = {state: [] for state in states}
    seen_keys = {state: set() for state in states}

    for b in qs.only("id", "broker_state", "broker_name", "broker_email", "broker_firm", "broker_city"):
        state = (b.broker_state or "").upper()
        if state not in results:
            continue
        key = (b.broker_email or "").lower().strip() or f"{(b.broker_name or '').strip()}|{(b.broker_firm or '').strip()}"
        if key in seen_keys[state]:
            continue
        seen_keys[state].add(key)
        results[state].append(
            {
                "id": b.id,
                "broker_name": b.broker_name,
                "broker_email": b.broker_email,
                "broker_firm": b.broker_firm,
                "broker_city": b.broker_city,
            }
        )

    return Response({"results": results}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Token-based uploads (public): Photos and Documents
# ---------------------------------------------------------------------------
# Docs reviewed:
# - DRF File uploads: https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser
# - DRF parser_classes decorator: https://www.django-rest-framework.org/api-guide/parsers/
# - Django files: https://docs.djangoproject.com/en/5.0/topics/files/


def _get_invite_and_broker_values_or_400(token: str):
    """Resolve an invite by token and return (invite, broker valuation instance).

    WHAT: Hub-first helper - resolve token to (invite, valuation)
    WHY: All file uploads need access to asset hub for storage
    HOW: Access hub directly via invite.asset_hub FK

    - 404 when token not found
    - 400 when expired
    - Ensures a Valuation (source='broker') instance exists for convenience
    """
    try:
        invite = BrokerTokenAuth.objects.get(token=token)
    except BrokerTokenAuth.DoesNotExist:
        return None, Response({"detail": "invalid_token"}, status=status.HTTP_404_NOT_FOUND)

    if invite.is_expired:
        return None, Response({"detail": "token_expired"}, status=status.HTTP_400_BAD_REQUEST)

    # WHAT: Access hub directly (hub-first)
    # WHY: All domain data through hub
    # HOW: invite.asset_hub FK
    hub = invite.asset_hub
    # Ensure a broker valuation exists (latest), create if none
    bv = (
        Valuation.objects
        .filter(asset_hub=hub, source='broker')
        .order_by('-value_date', '-created_at')
        .first()
    )
    if bv is None:
        bv = Valuation.objects.create(asset_hub=hub, source='broker')
    return (invite, bv), None


@api_view(["POST"])  # Public upload for broker photos (images only)
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_broker_photos_with_token(request, token: str):
    """Upload one or more image files as unified `Photo` records (source_tag='broker').

    Expected multipart form fields:
    - files: multiple file parts (preferred)
    - photos: alias for files
    - image: single image input (fallback)

    Returns JSON with uploaded count and URLs.
    """
    resolved, err = _get_invite_and_broker_values_or_400(token)
    if err is not None:
        return err
    _invite, bv = resolved

    # Get a list of files regardless of key used
    files = []
    # Prefer the canonical 'files' key
    files.extend(request.FILES.getlist("files"))
    # Support 'photos' as an alias
    if not files:
        files.extend(request.FILES.getlist("photos"))
    # Support 'image' as a fallback
    if not files:
        files.extend(request.FILES.getlist("image"))

    if not files:
        return Response({"detail": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

    created = []
    for f in files:
        # WHAT: Create unified Photo (hub-first); storage backend saves to MEDIA_ROOT
        # WHY: All attachments linked to hub for cross-module access
        # HOW: bv.asset_hub is the hub FK from Valuation
        p = Photo.objects.create(
            asset_hub=bv.asset_hub,
            source_raw_id=None,  # No longer using seller_raw_data_id
            image=f,
            source_tag='broker',
        )
        try:
            url = request.build_absolute_uri(p.image.url)
        except Exception:
            # If storage backend does not generate a URL, skip but keep record
            url = None
        created.append({
            'id': p.id,
            'url': url,
        })

    return Response({"uploaded": len(created), "items": created}, status=status.HTTP_201_CREATED)


@api_view(["POST"])  # Public upload for broker documents (any file type)
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def upload_broker_documents_with_token(request, token: str):
    """Upload one or more files as `Document` records bound to the token's asset hub.

    Expected multipart form fields:
    - files: multiple file parts (preferred)
      or
    - documents: multiple file parts (alias)

    Response 201:
    {
      "uploaded": <int>,
      "items": [{"id": <int>, "url": "https://...", "name": "original.ext"}]
    }
    """
    resolved, err = _get_invite_and_broker_values_or_400(token)
    if err is not None:
        return err
    _invite, bv = resolved

    files = []
    files.extend(request.FILES.getlist("files"))
    if not files:
        files.extend(request.FILES.getlist("documents"))

    if not files:
        return Response({"detail": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

    created = []
    for f in files:
        bd = Document.objects.create(
            asset_hub=bv.asset_hub,
            file=f,
            original_name=getattr(f, 'name', None),
        )
        try:
            url = request.build_absolute_uri(bd.file.url)
        except Exception:
            url = None
        created.append({"id": bd.id, "url": url, "name": bd.original_name})

    return Response({"uploaded": len(created), "items": created}, status=status.HTTP_201_CREATED)
