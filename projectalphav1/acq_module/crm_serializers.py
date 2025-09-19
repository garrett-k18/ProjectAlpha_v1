# projectalphav1/acq_module/crm_serializers.py
# Django REST Framework ModelSerializers for CRM models.
# Docs reviewed:
# - DRF ModelSerializer: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# - Field validation: https://www.django-rest-framework.org/api-guide/serializers/#validation
# - Partial updates: https://www.django-rest-framework.org/api-guide/serializers/#partial-updates

from rest_framework import serializers
from core.models.crm import Brokercrm, TradingPartnerCRM


class BrokercrmSerializer(serializers.ModelSerializer):
    """Serializer for the Brokercrm directory entries used by internal UI.

    Notes:
    - Includes simple read/write fields; leaves normalization (e.g., 2-letter state) to views/services as needed.
    - Using ModelSerializer ensures up-to-date fields without manual duplication.
    """

    class Meta:
        model = Brokercrm
        fields = [
            'id', 'broker_name', 'broker_email', 'broker_phone',
            'broker_firm', 'broker_city', 'broker_state', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TradingPartnerCRMSerializer(serializers.ModelSerializer):
    """Serializer for TradingPartnerCRM directory entries.

    Behaviors:
    - `firm` is required; all other fields are optional as per model definition.
    - `nda_signed` accepts YYYY-MM-DD format and returns ISO 8601 string.
    """

    class Meta:
        model = TradingPartnerCRM
        fields = [
            'id', 'firm', 'name', 'email', 'phone',
            'altname', 'altemail', 'alt_phone',
            'nda_flag', 'nda_signed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
