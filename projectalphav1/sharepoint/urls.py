"""
SharePoint API URL Configuration
=================================
Routes for SharePoint document access APIs.

Module: SharePoint
"""

from django.urls import path
from sharepoint.api import view_sp_documents

urlpatterns = [
    # Get asset-level documents
    path(
        'assets/<int:asset_hub_id>/documents/',
        view_sp_documents.get_asset_documents,
        name='asset_documents'
    ),
    
    # Get trade-level documents
    path(
        'trades/<int:trade_id>/documents/',
        view_sp_documents.get_trade_documents,
        name='trade_documents'
    ),
    
    # Upload file
    path(
        'upload/',
        view_sp_documents.upload_file,
        name='upload_file'
    ),
    
    # Get available tags
    path(
        'tags/',
        view_sp_documents.get_available_tags,
        name='available_tags'
    ),
]

