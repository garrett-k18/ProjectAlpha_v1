from __future__ import annotations

from rest_framework import serializers
from am_module.models.am_data import AMNote


class AMNoteSerializer(serializers.ModelSerializer):
    """Serializer for AMNote with user display fields.

    Returns author username and timestamps alongside the note body and tag.
    """

    created_by_username = serializers.SerializerMethodField(read_only=True)
    updated_by_username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AMNote
        fields = [
            "id",
            "asset_hub",
            "body",
            "tag",
            # context fields
            "scope",
            "context_outcome",
            "context_task_type",
            "context_task_id",
            "pinned",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "created_by_username",
            "updated_by_username",
        ]
        read_only_fields = [
            "asset_hub",
            "pinned",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "created_by_username",
            "updated_by_username",
        ]

    def get_created_by_username(self, obj: AMNote) -> str | None:
        u = getattr(obj.created_by, "username", None)
        return u

    def get_updated_by_username(self, obj: AMNote) -> str | None:
        u = getattr(obj.updated_by, "username", None)
        return u

    # Ensure created_by/updated_by are set from request user when available
    def create(self, validated_data):  # type: ignore[override]
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            validated_data.setdefault("created_by", user)
            validated_data.setdefault("updated_by", user)
        return super().create(validated_data)

    def update(self, instance: AMNote, validated_data):  # type: ignore[override]
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            validated_data["updated_by"] = user
        return super().update(instance, validated_data)
