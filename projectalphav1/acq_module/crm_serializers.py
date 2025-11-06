# projectalphav1/acq_module/crm_serializers.py
# Django REST Framework ModelSerializers for CRM models.
# Docs reviewed:
# - DRF ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# - Field validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
# - Partial updates: https://www.django-rest-framework.org/api-guide/serializers/#partial-updates

from rest_framework import serializers
from core.models.model_co_crm import MasterCRM


class BrokercrmSerializer(serializers.ModelSerializer):
    """Serializer for MasterCRM (legacy class name kept for API stability).

    Notes:
    - Includes simple read/write fields; leaves normalization (e.g., 2-letter state) to views/services as needed.
    - Using ModelSerializer ensures up-to-date fields without manual duplication.
    """

    class Meta:
        model = MasterCRM
        fields = [
            'id', 'firm', 'email', 'phone',
            'city', 'state', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
