"""
acq_module.serializers.asset_fc_timeline

What: Serializers for asset-scoped foreclosure timeline payloads.
Why: Provide a stable, typed contract to the frontend for state-specific FC durations.
Where: projectalphav1/acq_module/serializers/asset_fc_timeline.py
How: Two serializers - item (status row) and envelope (state + items).
"""
from rest_framework import serializers


class StatusTimelineItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    statusDisplay = serializers.CharField()
    durationDays = serializers.IntegerField(allow_null=True)


class AssetFCTimelineSerializer(serializers.Serializer):
    state = serializers.CharField(allow_null=True)
    statuses = StatusTimelineItemSerializer(many=True)
    totalDurationDays = serializers.IntegerField(allow_null=True)
    reoMarketingMonths = serializers.IntegerField(allow_null=True)
