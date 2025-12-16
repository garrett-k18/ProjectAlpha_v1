from __future__ import annotations

from rest_framework import serializers

from core.models import AssetIdHub
from core.models.model_core_notification import Notification


class NotificationSerializer(serializers.ModelSerializer):
    asset_hub_id = serializers.PrimaryKeyRelatedField(
        source="asset_hub",
        queryset=AssetIdHub.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    is_read = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "event_type",
            "title",
            "message",
            "asset_hub",
            "asset_hub_id",
            "created_by",
            "created_at",
            "metadata",
            "is_read",
        ]
        read_only_fields = ["id", "asset_hub", "created_by", "created_at", "is_read"]


class ActivityItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    source = serializers.CharField()  # notification | audit
    created_at = serializers.DateTimeField()

    title = serializers.CharField()
    message = serializers.CharField(allow_blank=True)

    event_type = serializers.CharField(required=False, allow_blank=True)
    field_name = serializers.CharField(required=False, allow_blank=True)
    old_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    new_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    asset_hub_id = serializers.IntegerField(required=False, allow_null=True)
    actor = serializers.CharField(required=False, allow_blank=True, allow_null=True)
