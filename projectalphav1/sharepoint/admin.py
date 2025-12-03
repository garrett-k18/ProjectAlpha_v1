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
        'uploaded_by',
        'uploaded_at',
        'is_validated',
    ]
    
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
            'fields': ('file_name', 'file_type', 'file_size_bytes', 'category')
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

