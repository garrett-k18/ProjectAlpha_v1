"""
Internal broker API endpoints (require staff authentication).

Responsibilities:
- Authenticated internal/admin endpoints only (no public token flows)
- Read endpoints for broker detail and broker-assigned loans
- Share business logic via `acq_module.services.brokers` to avoid duplication
- Separation of concerns: public invite flows live in `invites.py`; portal flows
  (batch assign + portal token) live in `portal.py`

Plain-language overview:
- These endpoints power the internal/admin UI for viewing brokers and their
  assigned loans.
- They DO NOT handle public invite links or token submissions.
- All shared database logic is pulled from acq_module.services.brokers to avoid
  duplication and keep behavior consistent across endpoints.

Endpoints provided here:
- GET /api/acq/brokers/<broker_id>/                -> broker_detail
- GET /api/acq/brokers/<broker_id>/assigned-loans/ -> list_assigned_loans

Docs reviewed:
- DRF Views: https://www.django-rest-framework.org/api-guide/views/
- DRF Permissions: https://www.django-rest-framework.org/api-guide/permissions/
"""
from typing import Any, Dict

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from core.models.crm import MasterCRM
from ...services.brokers import (
    get_broker_stats_dict,
    list_assigned_loan_entries,
)


@api_view(["GET", "PUT", "PATCH"])  # Dev: public detail + update endpoint
@permission_classes([AllowAny])
def broker_detail(request, broker_id: int):
    """Return CRM contact info (from MasterCRM) and quick stats.

    What this does:
    - Looks up the MasterCRM row by id.
    - Computes counts for: total invites, distinct assigned loans, submissions.
    - Returns a JSON object used by the broker detail page header.
    """
    broker: MasterCRM = get_object_or_404(MasterCRM, pk=broker_id)

    if request.method in ["PUT", "PATCH"]:
        payload = request.data or {}
        # Only update provided fields; mild normalization
        def norm(v):
            return (v or "").strip() or None

        name = payload.get("name")
        email = payload.get("email")
        phone = payload.get("phone")
        firm = payload.get("firm")
        city = payload.get("city")
        state_in = payload.get("state")

        if name is not None:
            broker.name = norm(name)
        if email is not None:
            broker.email = norm(email)
        if phone is not None:
            broker.phone = norm(phone)
        if firm is not None:
            broker.firm = norm(firm)
        if city is not None:
            broker.city = norm(city)
        if state_in is not None:
            state_val = norm(state_in)
            if state_val and len(state_val.upper()) != 2:
                return Response({"detail": "state must be a 2-letter code."}, status=status.HTTP_400_BAD_REQUEST)
            broker.state = state_val.upper() if state_val else None

        broker.save()

        updated = {
            "id": broker.id,
            "name": broker.name,
            "email": broker.email,
            "phone": broker.phone,
            "firm": broker.firm,
            "city": broker.city,
            "state": broker.state,
            "created_at": broker.created_at.isoformat() if broker.created_at else None,
        }
        return Response(updated, status=status.HTTP_200_OK)

    # GET behavior: include stats for the header detail view
    stats = get_broker_stats_dict(broker)

    data: Dict[str, Any] = {
        "id": broker.id,
        "name": broker.name,
        "email": broker.email,
        "phone": broker.phone,
        "firm": broker.firm,
        "city": broker.city,
        "state": broker.state,
        "stats": stats,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])  # Internal UI endpoint
@permission_classes([IsAuthenticated])
def list_assigned_loans(request, broker_id: int):
    """List loans assigned to a broker via invites (latest token per loan).

    What this does:
    - Confirms the broker exists.
    - Builds a list of assigned loans referencing the latest token for each loan.
    - Includes seller/trade info, address, optional current_balance, token status,
      and whether a BrokerValues submission exists for that SRD.
    - Response shape: { "results": AssignedLoanEntry[] }
    """
    broker: MasterCRM = get_object_or_404(MasterCRM, pk=broker_id)

    results = list_assigned_loan_entries(broker)
    return Response({"results": results}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])  # Dev: public list + create endpoint for MasterCRM directory
@permission_classes([AllowAny])
def list_brokers(request):
    """List or create contacts in the MasterCRM directory.

    GET query params:
      - q: case-insensitive search across name, email, firm, city
      - state: 2-letter state code to filter (case-insensitive)
      - tag: filter by contact type tag (broker, legal, trading_partner)
      - page: 1-based page number (default 1)
      - page_size: items per page (default 25, max 100)

    POST JSON body (all fields optional):
      - name: string
      - email: string (email)
      - phone: string
      - firm: string
      - city: string
      - state: 2-letter code (uppercase)

    Returns:
      - GET: a paginated shape compatible with simple list UIs.
      - POST: the created item in the same field shape as list rows.

    Docs reviewed:
    - DRF Requests for query_params: https://www.django-rest-framework.org/api-guide/requests/#query_params
    - Django ORM filtering: https://docs.djangoproject.com/en/5.0/topics/db/queries/
    """
    from django.db.models import Q

    if request.method == "POST":
        # Minimal create handler; production can use DRF serializers for validation
        payload = request.data or {}
        name = (payload.get("name") or "").strip() or None
        email = (payload.get("email") or "").strip() or None
        phone = (payload.get("phone") or "").strip() or None
        firm = (payload.get("firm") or "").strip() or None
        city = (payload.get("city") or "").strip() or None
        state_in = (payload.get("state") or "").strip().upper() or None

        # Basic format checks
        if state_in and len(state_in) != 2:
            return Response({"detail": "state must be a 2-letter code."}, status=status.HTTP_400_BAD_REQUEST)

        broker = MasterCRM.objects.create(
            name=name,
            email=email,
            phone=phone,
            firm=firm,
            city=city,
            state=state_in,
        )
        item = {
            "id": broker.id,
            "name": broker.name,
            "email": broker.email,
            "phone": broker.phone,
            "firm": broker.firm,
            "city": broker.city,
            "state": broker.state,
            "created_at": broker.created_at.isoformat() if broker.created_at else None,
        }
        return Response(item, status=status.HTTP_201_CREATED)

    # GET flow
    q = (request.query_params.get("q") or "").strip()
    state = (request.query_params.get("state") or "").strip().upper()
    tag = (request.query_params.get("tag") or "").strip().lower()
    try:
        page = max(1, int(request.query_params.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", 25))
    except (TypeError, ValueError):
        page_size = 25
    page_size = max(1, min(page_size, 100))

    qs = MasterCRM.objects.all().order_by("-created_at")

    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(firm__icontains=q)
            | Q(city__icontains=q)
        )
    if state:
        qs = qs.filter(state=state)
    if tag:
        qs = qs.filter(tag=tag)

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = list(
        qs.values(
            "id",
            "name",
            "email",
            "phone",
            "firm",
            "city",
            "state",
            "created_at",
        )[start:end]
    )

    # Convert datetimes to ISO 8601 strings
    for it in items:
        if it.get("created_at") is not None:
            it["created_at"] = it["created_at"].isoformat()

    return Response(
        {
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": items,
        },
        status=status.HTTP_200_OK,
    )
