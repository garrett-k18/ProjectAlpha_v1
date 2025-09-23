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
