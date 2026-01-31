"""
Broker portal endpoints: assign brokers in batch and serve a single broker portal URL.

Responsibilities:
- Internal batch assignment from AG Grid to a single broker (creates multiple invites)
- Maintain/return a single reusable portal token per broker (non-expired)
- Public portal fetch by portal token to show active invites
- Separation of concerns: single-invite flows live in `invites.py`; internal non-portal
  broker reads live in `internal.py`

Endpoints provided here:
- POST /api/acq/broker-portal/assign/      -> assign_broker_batch (internal)
- GET  /api/acq/broker-portal/<token>/     -> broker_portal_detail (public)

Docs reviewed:
- DRF Views/Permissions/Serializers
  https://www.django-rest-framework.org/api-guide/views/
  https://www.django-rest-framework.org/api-guide/permissions/
  https://www.django-rest-framework.org/api-guide/serializers/
- Django ORM queries
  https://docs.djangoproject.com/en/5.0/topics/db/queries/
"""
from datetime import timedelta
from typing import List

from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny  # TODO: tighten to IsAuthenticated for internal endpoints
from rest_framework.response import Response
from rest_framework import status, serializers

from core.models.model_co_valuations import Valuation
from core.models.model_co_crm import MasterCRM
from ...services.brokers import list_assigned_loan_entries
from user_admin.models import BrokerTokenAuth
from user_admin.models.externalauth import BrokerPortalToken


class AssignBrokerSerializer(serializers.Serializer):
    broker_id = serializers.IntegerField()
    # WHAT: Asset hub IDs for assignment (same values as seller_raw_data IDs since SRD uses hub as PK)
    # WHY: Hub-first architecture - all assignments through AssetIdHub
    # HOW: Accept either field name for backward compatibility
    seller_raw_data_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=False)
    asset_hub_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False, required=False)
    # Optional overrides
    expires_in_hours = serializers.IntegerField(required=False)  # invites default
    portal_expires_in_hours = serializers.IntegerField(required=False)  # portal default
    
    def validate(self, data):
        # WHAT: Ensure at least one ID list is provided
        # WHY: Support both old (seller_raw_data_ids) and new (asset_hub_ids) field names
        # HOW: Use whichever is provided; prefer asset_hub_ids if both present
        if not data.get('asset_hub_ids') and not data.get('seller_raw_data_ids'):
            raise serializers.ValidationError("Either asset_hub_ids or seller_raw_data_ids required")
        # Normalize to asset_hub_ids internally
        if not data.get('asset_hub_ids'):
            data['asset_hub_ids'] = data.get('seller_raw_data_ids', [])
        return data


@api_view(["POST"])  # internal use; open for now
@permission_classes([AllowAny])
def assign_broker_batch(request):
    """Assign a broker to many assets and create tokens.

    WHAT: Hub-first architecture - assign brokers to AssetIdHub IDs
    WHY: All joins happen through AssetIdHub intentionally
    HOW: Accept asset_hub_ids (or seller_raw_data_ids for backward compat since they're the same value)

    Body:
    {
      "broker_id": 123,
      "asset_hub_ids": [1143,1144,1145],      # preferred (hub-first)
      "seller_raw_data_ids": [1143,1144,1145],  # backward compat (same values)
      "expires_in_hours": 360,                  # optional, default 360 (15 days)
      "portal_expires_in_hours": 360            # optional, default 360 (15 days)
    }

    Behavior:
    - Ensure a valid (non-expired) portal token exists for the broker; create if needed.
    - For each asset hub ID provided, create a new BrokerTokenAuth token linked to broker.
    - Return portal token info and created invites summary.
    """
    serializer = AssignBrokerSerializer(data=request.data or {})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    broker: MasterCRM = get_object_or_404(MasterCRM, pk=data["broker_id"]) 
    # WHAT: Get asset hub IDs (normalized from either field name in serializer)
    hub_ids: List[int] = data["asset_hub_ids"]

    invite_hours = int(data.get("expires_in_hours") or 360)
    portal_hours = int(data.get("portal_expires_in_hours") or 360)

    # WHAT: Ensure a valid portal token exists (latest non-expired or create new)
    # WHY: One portal URL per broker shows all their assignments
    # HOW: Query latest non-expired token or create if none found
    now = timezone.now()
    portal = (
        BrokerPortalToken.objects.filter(broker=broker, expires_at__gt=now)
        .order_by("-created_at")
        .first()
    )
    if not portal:
        # create new portal token
        token = BrokerPortalToken.generate_token()
        while BrokerPortalToken.objects.filter(token=token).exists():
            token = BrokerPortalToken.generate_token()
        portal = BrokerPortalToken.objects.create(
            broker=broker,
            token=token,
            expires_at=now + timedelta(hours=portal_hours),
        )

    # WHAT: Create invites per asset hub
    # WHY: Hub-first architecture - tokens point to asset hubs
    # HOW: Fetch hub, create BrokerTokenAuth with asset_hub FK
    from core.models.model_co_assetIdHub import AssetIdHub
    invites = []
    for hub_id in hub_ids:
        hub = get_object_or_404(AssetIdHub, pk=hub_id)
        token = BrokerTokenAuth.generate_token()
        while BrokerTokenAuth.objects.filter(token=token).exists():
            token = BrokerTokenAuth.generate_token()
        invite = BrokerTokenAuth.objects.create(
            asset_hub=hub,
            broker=broker,
            token=token,
            expires_at=now + timedelta(hours=invite_hours),
            # Portal invites must be multi-use until expiration
            single_use=False,
        )
        invites.append(
            {
                "asset_hub_id": invite.asset_hub_id,
                "seller_raw_data": invite.asset_hub_id,  # Backward compat (same value)
                "token": invite.token,
                "expires_at": invite.expires_at.isoformat(),
            }
        )

    return Response(
        {
            "portal": {
                "token": portal.token,
                "expires_at": portal.expires_at.isoformat(),
                "url": f"/brokerview/{portal.token}",
            },
            "invites": invites,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])  # public broker portal endpoint
@permission_classes([AllowAny])
def broker_portal_detail(request, token: str):
    """Return broker portal context and active invites by portal token.

    Response 200:
    {
      "valid": true,
      "broker": {"id": ..., "broker_name": ..., "broker_email": ..., "broker_firm": ...},
      "expires_at": "ISO",
      "active_invites": [ entries... ]
    }
    
    Note: broker_name/email/firm are mapped from MasterCRM.contact_name/email/firm

    404 if token not found; 400 if expired.
    """
    try:
        portal = BrokerPortalToken.objects.select_related("broker").get(token=token)
    except BrokerPortalToken.DoesNotExist:
        return Response({"valid": False, "reason": "not_found"}, status=status.HTTP_404_NOT_FOUND)

    if portal.is_expired:
        return Response({"valid": False, "reason": "expired", "expires_at": portal.expires_at.isoformat()}, status=status.HTTP_400_BAD_REQUEST)

    broker = portal.broker

    # WHAT: Build entries using shared service (hub-first)
    # WHY: Centralized logic for listing broker assignments
    # HOW: Service returns entries with asset_hub_id and seller_raw_data (same value)
    entries = list_assigned_loan_entries(broker)

    # WHAT: Enrich with any saved broker Valuation so the UI can prefill even if the invite is expired/used
    # WHY: Preserves previously submitted values in the portal for UX continuity
    # HOW: Map Valuation by asset_hub_id (hub-first query)
    hub_ids = [e.get("asset_hub_id") for e in entries if e.get("asset_hub_id") is not None]
    values_by_hub = {}
    for bv in (
        Valuation.objects
        .filter(asset_hub_id__in=hub_ids, source='broker')
        .order_by('-value_date', '-created_at')
    ):
        values_by_hub[bv.asset_hub_id] = bv

    enriched_entries = []
    for e in entries:
        hub_id = e.get("asset_hub_id")
        bv = values_by_hub.get(hub_id)
        if bv:
            # WHAT: Serialize grade FK to code string
            # WHY: grade is a ForeignKey to ValuationGradeReference, need to extract code for JSON
            # HOW: Access grade.code if grade FK is populated
            grade_obj = getattr(bv, "grade", None)
            grade_code = getattr(grade_obj, "code", None) if grade_obj else None
            
            e = {
                **e,
                "values": {
                    # Back-compat keys mapped from unified Valuation
                    "broker_asis_value": str(getattr(bv, 'asis_value', None)) if getattr(bv, 'asis_value', None) is not None else None,
                    "broker_arv_value": str(getattr(bv, 'arv_value', None)) if getattr(bv, 'arv_value', None) is not None else None,
                    "broker_rehab_est": str(getattr(bv, 'rehab_est_total', None)) if getattr(bv, 'rehab_est_total', None) is not None else None,
                    "broker_value_date": getattr(bv, 'value_date', None).isoformat() if getattr(bv, 'value_date', None) else None,
                    "broker_notes": getattr(bv, "notes", None),
                    "broker_grade": grade_code,  # WHAT: Grade code string (A+, A, B, etc.) for JSON serialization
                    # WHAT: Detailed rehab breakdown by trade category
                    # WHY: Support inspection report modal in broker portal
                    # HOW: Include all grade and cost estimate fields for each trade
                    "broker_roof_grade": getattr(bv, 'broker_roof_grade', None),
                    "broker_roof_est": getattr(bv, 'broker_roof_est', None),
                    "broker_kitchen_grade": getattr(bv, 'broker_kitchen_grade', None),
                    "broker_kitchen_est": getattr(bv, 'broker_kitchen_est', None),
                    "broker_bath_grade": getattr(bv, 'broker_bath_grade', None),
                    "broker_bath_est": getattr(bv, 'broker_bath_est', None),
                    "broker_flooring_grade": getattr(bv, 'broker_flooring_grade', None),
                    "broker_flooring_est": getattr(bv, 'broker_flooring_est', None),
                    "broker_windows_grade": getattr(bv, 'broker_windows_grade', None),
                    "broker_windows_est": getattr(bv, 'broker_windows_est', None),
                    "broker_appliances_grade": getattr(bv, 'broker_appliances_grade', None),
                    "broker_appliances_est": getattr(bv, 'broker_appliances_est', None),
                    "broker_plumbing_grade": getattr(bv, 'broker_plumbing_grade', None),
                    "broker_plumbing_est": getattr(bv, 'broker_plumbing_est', None),
                    "broker_electrical_grade": getattr(bv, 'broker_electrical_grade', None),
                    "broker_electrical_est": getattr(bv, 'broker_electrical_est', None),
                    "broker_landscaping_grade": getattr(bv, 'broker_landscaping_grade', None),
                    "broker_landscaping_est": getattr(bv, 'broker_landscaping_est', None),
                },
            }
        enriched_entries.append(e)

    # Filter to active invites for submission ability
    # Requirement: Portal invites remain usable until expiration, regardless of prior submissions.
    active_entries = [
        e for e in enriched_entries
        if not e["token"]["is_expired"]
    ]

    return Response(
        {
            "valid": True,
            "broker": {
                "id": broker.id,
                # WHAT: MasterCRM field names (not old broker-specific names)
                # WHY: MasterCRM uses contact_name, email, firm (unified CRM)
                # HOW: Map to backward-compatible keys for frontend
                "broker_name": broker.contact_name,  # MasterCRM.contact_name
                "broker_email": broker.email,         # MasterCRM.email
                "broker_firm": broker.firm,           # MasterCRM.firm
            },
            "expires_at": portal.expires_at.isoformat(),
            # Active invites allow saving (contain valid token)
            "active_invites": active_entries,
            # Assigned entries include latest per SRD regardless of token status,
            # enriched with any saved values to display after submission/expiry.
            "assigned_entries": enriched_entries,
        },
        status=status.HTTP_200_OK,
    )
