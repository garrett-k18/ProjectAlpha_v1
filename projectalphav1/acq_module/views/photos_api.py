"""
Photos API endpoints for acquisitions module.

Docs checked:
- Django REST Framework API Guide: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- Django File storage & MEDIA_URL: https://docs.djangoproject.com/en/5.2/topics/files/

This module exposes a single GET endpoint to list all photos (Public, Document, Broker)
associated with a given SellerRawData id. It normalizes results to a frontend-friendly
format: [{ src, alt?, thumb? }].

We build absolute URLs using request.build_absolute_uri(photo.url) so the Vue app can
render images from any device (LAN/non-VPN) without needing to hardcode a host.
"""
from typing import List, Dict

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers

from ..models.seller import SellerRawData
from ..models.valuations import PublicPhoto, DocumentPhoto, BrokerPhoto


class OutputPhotoSerializer(serializers.Serializer):
    """Serializer for normalized photo output expected by the Vue PhotoCarousel.
    Fields:
    - src: absolute URL to the image
    - alt: optional alt/caption text
    - thumb: optional thumbnail URL (defaults to src on the frontend if omitted)
    """
    src = serializers.CharField()
    alt = serializers.CharField(required=False, allow_blank=True)
    thumb = serializers.CharField(required=False, allow_blank=True)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_photos_by_raw_id(request, id: int):
    """Return all photos for a given SellerRawData id in a normalized structure.

    URL: /api/acq/photos/<id>/
    Path params:
      - id: SellerRawData primary key.

    Response: 200 OK
    [
      {"src": "https://host/media/...", "alt": "Public photo (Google)", "thumb": "..."},
      {"src": "https://host/media/...", "alt": "Document photo p3", "thumb": "..."},
      {"src": "https://host/media/...", "alt": "Broker photo", "thumb": "..."}
    ]
    """
    # Ensure the parent record exists; router will place SellerRawData reads into seller_data DB
    raw = get_object_or_404(SellerRawData, pk=id)

    # Helper to build absolute URLs from storage-relative .url
    def abs_url(rel_url: str) -> str:
        return request.build_absolute_uri(rel_url)

    items: List[Dict] = []

    # Public photos (scraped)
    for p in PublicPhoto.objects.filter(seller_raw_data=raw).iterator():
        try:
            src = abs_url(p.photo.url)
        except Exception:
            # Skip records with missing files
            continue
        alt = f"Public photo ({p.get_source_display()})" if hasattr(p, "get_source_display") else "Public photo"
        items.append({
            "src": src,
            "alt": p.caption or alt,
            "thumb": src,
        })

    # Document photos (extracted)
    for d in DocumentPhoto.objects.filter(seller_raw_data=raw).iterator():
        try:
            src = abs_url(d.photo.url)
        except Exception:
            continue
        page = f" p{d.page_number}" if d.page_number is not None else ""
        alt = d.caption or f"Document photo{page}"
        items.append({
            "src": src,
            "alt": alt,
            "thumb": src,
        })

    # Broker photos (via BrokerValues -> SellerRawData)
    for b in BrokerPhoto.objects.filter(broker_valuation__seller_raw_data=raw).iterator():
        try:
            src = abs_url(b.photo.url)
        except Exception:
            continue
        items.append({
            "src": src,
            "alt": "Broker photo",
            "thumb": src,
        })

    # Serialize to enforce output contract (and future-proof additional validation)
    data = OutputPhotoSerializer(items, many=True).data
    return Response(data, status=status.HTTP_200_OK)
