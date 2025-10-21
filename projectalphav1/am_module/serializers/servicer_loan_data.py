from __future__ import annotations

from rest_framework import serializers
from am_module.models.servicers import ServicerLoanData


class ServicerLoanDataSerializer(serializers.ModelSerializer):
    """Serializer for the ServicerLoanData model.

    This serializer includes all fields from the ServicerLoanData model, making it
    suitable for detail views where all data for a single record is required.
    """

    # Frontend-friendly aliases
    as_of = serializers.DateField(source='as_of_date', read_only=True)

    asset_hub_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ServicerLoanData
        fields = '__all__'
