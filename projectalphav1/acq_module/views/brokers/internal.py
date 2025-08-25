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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ...models import Brokercrm
from ...services.brokers import (
    get_broker_stats_dict,
    list_assigned_loan_entries,
)


@api_view(["GET"])  # Internal UI endpoint
@permission_classes([IsAuthenticated])
def broker_detail(request, broker_id: int):
    """Return broker directory info (from Brokercrm) and quick stats.

    What this does:
    - Looks up the Brokercrm row by id.
    - Computes counts for: total invites, distinct assigned loans, submissions.
    - Returns a JSON object used by the broker detail page header.
    """
    broker = get_object_or_404(Brokercrm, pk=broker_id)

    stats = get_broker_stats_dict(broker)

    data: Dict[str, Any] = {
        "id": broker.id,
        "broker_name": broker.broker_name,
        "broker_email": broker.broker_email,
        "broker_firm": broker.broker_firm,
        "broker_city": broker.broker_city,
        "broker_state": broker.broker_state,
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
    broker = get_object_or_404(Brokercrm, pk=broker_id)

    results = list_assigned_loan_entries(broker)
    return Response({"results": results}, status=status.HTTP_200_OK)
