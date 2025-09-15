"""
Trading partner API endpoints using DRF + ModelSerializer.

Responsibilities:
- Public list/create and retrieve/update endpoints for TradingPartnerCRM.
- Validation and (de)serialization handled by TradingPartnerCRMSerializer.

Docs reviewed:
- DRF @api_view: https://www.django-rest-framework.org/api-guide/views/#function-based-views
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Responses/Request: https://www.django-rest-framework.org/api-guide/requests/
"""
from typing import Any, Dict

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models import TradingPartnerCRM
from ..serializers import TradingPartnerCRMSerializer


@api_view(["GET", "POST"])  # Dev: public list + create endpoint
@permission_classes([AllowAny])
def list_trading_partners(request):
    """List or create trading partners.

    GET query params:
      - q: case-insensitive search across firm, name, email, altemail, phone, alt_phone
      - page: 1-based page number (default 1)
      - page_size: items per page (default 25, max 100)

    POST JSON body:
      - firm (required)
      - name, email, phone, altname, altemail, alt_phone, nda_flag, nda_signed (optional)

    Returns:
      - GET: a paginated shape compatible with list UIs.
      - POST: the created item in the same field shape as list rows.
    """
    if request.method == "POST":
        # Use serializer for validation/creation; firm is required by model
        serializer = TradingPartnerCRMSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(TradingPartnerCRMSerializer(instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # GET flow
    q = (request.query_params.get("q") or "").strip()
    try:
        page = max(1, int(request.query_params.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = int(request.query_params.get("page_size", 25))
    except (TypeError, ValueError):
        page_size = 25
    page_size = max(1, min(page_size, 100))

    qs = TradingPartnerCRM.objects.all().order_by("-created_at")

    if q:
        qs = qs.filter(
            Q(firm__icontains=q)
            | Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(altemail__icontains=q)
            | Q(phone__icontains=q)
            | Q(alt_phone__icontains=q)
        )

    total = qs.count()
    start = (page - 1) * page_size
    end = start + page_size
    items = qs[start:end]

    data = TradingPartnerCRMSerializer(items, many=True).data

    return Response(
        {
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "PATCH"])  # Dev: public detail + partial update endpoint
@permission_classes([AllowAny])
def trading_partner_detail(request, partner_id: int):
    """Retrieve or update a single trading partner by id.

    PATCH JSON body supports partial updates with the same fields as POST.
    """
    partner = get_object_or_404(TradingPartnerCRM, pk=partner_id)

    if request.method == "PATCH":
        serializer = TradingPartnerCRMSerializer(partner, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(TradingPartnerCRMSerializer(instance).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(TradingPartnerCRMSerializer(partner).data, status=status.HTTP_200_OK)
