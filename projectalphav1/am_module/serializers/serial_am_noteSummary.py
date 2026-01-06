"""
Serializer for AM Note Summary.

WHAT: Serializes AMNoteSummary model for API responses.
WHY: Provides clean API interface for note summaries.
HOW: Thin wrapper around model, extracts summary_data fields.
"""

from rest_framework import serializers
from am_module.models.model_am_amData import AMNoteSummary


class AMNoteSummarySerializer(serializers.ModelSerializer):
    """
    WHAT: Serializer for AMNoteSummary with flattened summary data.
    WHY: Frontend expects summary_text and bullets at top level, not nested in summary_data.
    HOW: Uses SerializerMethodField to extract from summary_data JSON field.
    """
    
    # WHAT: Flattened fields from summary_data JSON
    # WHY: Frontend expects these at top level for easier access
    # HOW: Extract from summary_data dict using SerializerMethodField
    summary_text = serializers.SerializerMethodField()
    bullets = serializers.SerializerMethodField()
    note_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AMNoteSummary
        fields = [
            "id",
            "asset_hub",
            "summary_text",
            "bullets",
            "note_count",
            "generated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "asset_hub",
            "summary_text",
            "bullets",
            "note_count",
            "generated_at",
            "created_at",
            "updated_at",
        ]
    
    def get_summary_text(self, obj: AMNoteSummary) -> str:
        """
        WHAT: Extracts summary_text from summary_data JSON field.
        WHY: Frontend expects this at top level.
        HOW: Access summary_data dict and return summary_text value.
        """
        # WHAT: Get summary_data dict from model instance
        # WHY: summary_text is stored in JSON field
        # HOW: Access summary_data attribute
        summary_data = getattr(obj, 'summary_data', {}) or {}
        
        # WHAT: Return summary_text or empty string
        # WHY: Provide fallback if field missing
        # HOW: Use dict.get with default
        return summary_data.get('summary_text', '')
    
    def get_bullets(self, obj: AMNoteSummary) -> list:
        """
        WHAT: Extracts bullets array from summary_data JSON field.
        WHY: Frontend expects this at top level.
        HOW: Access summary_data dict and return bullets value.
        """
        # WHAT: Get summary_data dict from model instance
        # WHY: bullets are stored in JSON field
        # HOW: Access summary_data attribute
        summary_data = getattr(obj, 'summary_data', {}) or {}
        
        # WHAT: Return bullets list or empty list
        # WHY: Provide fallback if field missing
        # HOW: Use dict.get with default
        return summary_data.get('bullets', [])
    
    def get_note_count(self, obj: AMNoteSummary) -> int:
        """
        WHAT: Extracts note_count from summary_data JSON field.
        WHY: Frontend may want to display how many notes were summarized.
        HOW: Access summary_data dict and return note_count value.
        """
        # WHAT: Get summary_data dict from model instance
        # WHY: note_count is stored in JSON field
        # HOW: Access summary_data attribute
        summary_data = getattr(obj, 'summary_data', {}) or {}
        
        # WHAT: Return note_count or 0
        # WHY: Provide fallback if field missing
        # HOW: Use dict.get with default
        return summary_data.get('note_count', 0)

