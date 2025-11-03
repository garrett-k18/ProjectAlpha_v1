"""
Document Management API Views
Provides REST API endpoints for Vue frontend to interact with Egnyte document storage.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
from core.services.serv_co_egnyteDoc import egnyte_service
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """
    Upload a document to Egnyte.
    
    Expected request:
    - file: The document file
    - folder_path: (optional) Destination folder path
    
    Returns:
    - success: boolean
    - path: file path in Egnyte
    - message: status message
    """
    try:
        # Get the uploaded file
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'success': False, 'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional folder path
        folder_path = request.data.get('folder_path', '/Shared/Documents')
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Upload to Egnyte
        result = egnyte_service.upload_file(
            file_path=uploaded_file.name,
            file_content=file_content,
            folder_path=folder_path
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in upload_document: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    List documents in a folder.
    
    Query params:
    - folder_path: Path to folder (default: /Shared)
    
    Returns:
    - success: boolean
    - data: folder contents (files and subfolders)
    """
    try:
        folder_path = request.query_params.get('folder_path', '/Shared')
        result = egnyte_service.list_folder(folder_path)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in list_documents: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document(request):
    """
    Download a document from Egnyte.
    
    Query params:
    - file_path: Path to the file
    
    Returns:
    - File content as HTTP response
    """
    try:
        file_path = request.query_params.get('file_path')
        if not file_path:
            return Response(
                {'success': False, 'error': 'file_path parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_content = egnyte_service.download_file(file_path)
        
        if file_content:
            from django.http import HttpResponse
            response = HttpResponse(file_content, content_type='application/octet-stream')
            filename = file_path.split('/')[-1]
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return Response(
                {'success': False, 'error': 'File not found or error downloading'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    except Exception as e:
        logger.error(f"Error in download_document: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request):
    """
    Delete a document from Egnyte.
    
    Request body:
    - file_path: Path to the file to delete
    
    Returns:
    - success: boolean
    - message: status message
    """
    try:
        file_path = request.data.get('file_path')
        if not file_path:
            return Response(
                {'success': False, 'error': 'file_path required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = egnyte_service.delete_file(file_path)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in delete_document: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_folder(request):
    """
    Create a new folder in Egnyte.
    
    Request body:
    - folder_path: Path for the new folder
    
    Returns:
    - success: boolean
    - path: created folder path
    - message: status message
    """
    try:
        folder_path = request.data.get('folder_path')
        if not folder_path:
            return Response(
                {'success': False, 'error': 'folder_path required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = egnyte_service.create_folder(folder_path)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in create_folder: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_documents(request):
    """
    Search for documents in Egnyte.
    
    Query params:
    - query: Search query string
    - folder_path: (optional) Folder to search in
    
    Returns:
    - success: boolean
    - results: array of matching files
    """
    try:
        query = request.query_params.get('query')
        if not query:
            return Response(
                {'success': False, 'error': 'query parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        folder_path = request.query_params.get('folder_path', '/Shared')
        result = egnyte_service.search_files(query, folder_path)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in search_documents: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_share_link(request):
    """
    Create a shareable link for a file or folder.
    
    Request body:
    - file_path: Path to the file/folder
    - link_type: 'file' or 'folder'
    - expiry_date: (optional) Expiry date in YYYY-MM-DD format
    
    Returns:
    - success: boolean
    - link: shareable URL
    """
    try:
        file_path = request.data.get('file_path')
        if not file_path:
            return Response(
                {'success': False, 'error': 'file_path required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        link_type = request.data.get('link_type', 'file')
        expiry_date = request.data.get('expiry_date')
        
        result = egnyte_service.create_link(file_path, link_type, expiry_date)
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error in create_share_link: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_file_info(request):
    """
    Get metadata for a specific file.
    
    Query params:
    - file_path: Path to the file
    
    Returns:
    - success: boolean
    - data: file metadata (size, dates, etc.)
    """
    try:
        file_path = request.query_params.get('file_path')
        if not file_path:
            return Response(
                {'success': False, 'error': 'file_path parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = egnyte_service.get_file_info(file_path)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Error in get_file_info: {str(e)}")
        return Response(
            {'success': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

