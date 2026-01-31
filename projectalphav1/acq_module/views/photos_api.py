"""
Photos API endpoints for acquisitions module.

Docs checked:
- Django REST Framework API Guide: https://www.django-rest-framework.org/api-guide/views/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- Django File storage & MEDIA_URL: https://docs.djangoproject.com/en/5.2/topics/files/

This module exposes a single GET endpoint to list all photos (Public, Document, Broker)
associated with a given SellerRawData id. Under the hub-first model, photos belong to
AssetIdHub; we resolve the hub from the SellerRawData row and return all photos for that hub.
It normalizes results to a frontend-friendly
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

from ..models.model_acq_seller import AcqAsset
from core.models.attachments import Photo


class OutputPhotoSerializer(serializers.Serializer):
    """Serializer for normalized photo output expected by the Vue PhotoCarousel.
    Fields:
    - src: absolute URL to the image
    - alt: optional alt/caption text
    - thumb: optional thumbnail URL (defaults to src on the frontend if omitted)
    - type: optional discriminator for source category (public|document|broker)

    Docs reviewed:
    - DRF Serializer fields: https://www.django-rest-framework.org/api-guide/serializers/#declaring-serializers
    Adding an optional field is backward-compatible for existing clients.
    """
    src = serializers.CharField()
    alt = serializers.CharField(required=False, allow_blank=True)
    thumb = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_photos_by_raw_id(request, id: int):
    """Return all photos for a given asset id in a normalized structure.

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
    # Ensure the parent record exists; router will place AcqAsset reads into seller_data DB
    asset = get_object_or_404(AcqAsset, pk=id)

    # Helper to build absolute URLs from storage-relative .url
    def abs_url(rel_url: str) -> str:
        return request.build_absolute_uri(rel_url)

    items: List[Dict] = []

    # Unified photos for the owning hub
    hub = getattr(asset, 'asset_hub', None)
    qs = Photo.objects.none()
    if hub is not None:
        qs = Photo.objects.filter(asset_hub=hub)

    for p in qs.iterator():
        try:
            src = abs_url(p.image.url)
        except Exception:
            # Skip records with missing files
            continue

        # Derive alt text based on source_tag and available metadata
        if p.source_tag == 'public':
            alt = p.caption or "Public photo"
        elif p.source_tag == 'document':
            page = f" p{p.page_number}" if p.page_number is not None else ""
            alt = p.caption or f"Document photo{page}"
        elif p.source_tag == 'broker':
            alt = p.caption or "Broker photo"
        else:
            alt = p.caption or "Photo"

        items.append({
            "src": src,
            "alt": alt,
            "thumb": src,
            "type": p.source_tag,
        })

    # Serialize to enforce output contract (and future-proof additional validation)
    data = OutputPhotoSerializer(items, many=True).data
    return Response(data, status=status.HTTP_200_OK)
