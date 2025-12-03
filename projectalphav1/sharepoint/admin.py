from django.contrib import admin
from sharepoint.models import SharePointDocument


@admin.register(SharePointDocument)
class SharePointDocumentAdmin(admin.ModelAdmin):
    """Admin interface for SharePoint documents"""
    
    list_display = [
        'file_name',
        'trade_id',
        'asset_id',
        'category',
        'get_tags_display',
        'uploaded_by',
        'uploaded_at',
        'is_validated',
    ]
    
    def get_tags_display(self, obj):
        """Display tags as comma-separated list"""
        return ', '.join(obj.tags) if obj.tags else '-'
    get_tags_display.short_description = 'Tags'
    
    list_filter = [
        'category',
        'is_validated',
        'is_deleted',
        'uploaded_at',
    ]
    
    search_fields = [
        'file_name',
        'trade_id',
        'asset_id',
        'sharepoint_path',
    ]
    
    readonly_fields = [
        'sharepoint_item_id',
        'sharepoint_drive_id',
        'sharepoint_web_url',
        'uploaded_at',
        'last_modified_at',
    ]
    
    fieldsets = (
        ('Document Info', {
            'fields': ('file_name', 'file_type', 'file_size_bytes', 'category', 'tags')
        }),
        ('Location', {
            'fields': ('trade_id', 'asset_id')
        }),
        ('SharePoint', {
            'fields': (
                'sharepoint_path',
                'sharepoint_item_id',
                'sharepoint_drive_id',
                'sharepoint_web_url',
            )
        }),
        ('Validation', {
            'fields': ('is_validated', 'validation_errors')
        }),
        ('Audit', {
            'fields': ('uploaded_by', 'uploaded_at', 'last_modified_at')
        }),
        ('Status', {
            'fields': ('is_deleted', 'deleted_at')
        }),
    )
    
    def get_queryset(self, request):
        """Only show non-deleted by default"""
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

