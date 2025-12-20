"""
Awarded Assets API Views

WHAT: API endpoints for awarded assets workflow
WHY: Allow users to upload awarded lists and drop non-awarded assets
HOW: DRF APIView with file upload and confirmation endpoints

USAGE:
    POST /api/acq/awarded-assets/upload/
    POST /api/acq/awarded-assets/preview/
    POST /api/acq/awarded-assets/confirm/
    POST /api/acq/awarded-assets/undo/
    GET  /api/acq/awarded-assets/history/{trade_id}/

Docs reviewed:
- DRF APIView: https://www.django-rest-framework.org/api-guide/views/
- File uploads: https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser
"""

import logging
import mimetypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings

from acq_module.services.serv_acq_awarded_assets import AwardedAssetsService
from acq_module.serializers.serial_acq_awarded_assets import (
    FileUploadSerializer,
    ExtractionResponseSerializer,
    PreviewResponseSerializer,
    ConfirmDropSerializer,
    ExecuteResponseSerializer,
    UndoDropSerializer,
    UndoResponseSerializer,
    DropHistorySerializer,
)

logger = logging.getLogger(__name__)


class UploadAwardedAssetsView(APIView):
    """
    WHAT: Upload file with awarded asset IDs and extract using AI
    WHY: First step in awarded assets workflow
    HOW: Accept file upload, send to Claude, return extracted IDs
    
    POST /api/acq/awarded-assets/upload/
    Content-Type: multipart/form-data
    Body:
        file: <file>
        trade_id: <int>
    
    Response:
        {
            "identifiers": ["ABC123", ...],
            "confidence": "high",
            "detected_format": "...",
            "count": 250
        }
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def get_permissions(self):
        """
        WHAT: Bypass auth in DEBUG mode for development
        WHY: Easier testing during development
        HOW: Return empty list if DEBUG=True
        """
        if settings.DEBUG:
            return []
        return [IsAuthenticated()]
    
    def post(self, request):
        """
        WHAT: Handle file upload and AI extraction
        WHY: Extract awarded IDs from any file format
        HOW: Validate, read file, call service, return results
        """
        # WHAT: Validate request data
        # WHY: Ensure we have required fields
        # HOW: Use serializer
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trade_id = serializer.validated_data['trade_id']
        uploaded_file = serializer.validated_data['file']
        
        logger.info(
            f"Processing awarded assets upload for trade {trade_id}: "
            f"{uploaded_file.name} ({uploaded_file.size} bytes)"
        )
        
        try:
            # WHAT: Read file bytes
            # WHY: Need raw bytes for Claude API
            # HOW: Read entire file into memory
            file_bytes = uploaded_file.read()
            
            # WHAT: Detect MIME type
            # WHY: Claude needs to know file format
            # HOW: Use mimetypes module with fallbacks
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            if not mime_type:
                # Fallback based on extension
                ext = uploaded_file.name.lower().split('.')[-1]
                mime_map = {
                    'pdf': 'application/pdf',
                    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'xls': 'application/vnd.ms-excel',
                    'csv': 'text/csv',
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                }
                mime_type = mime_map.get(ext, 'application/octet-stream')
            
            # WHAT: Initialize service and extract IDs
            # WHY: Use service layer for business logic
            # HOW: Create service instance and call extract method
            service = AwardedAssetsService(trade_id=trade_id)
            result = service.extract_ids_from_file(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                mime_type=mime_type
            )
            
            # WHAT: Check for errors
            # WHY: Return appropriate status code
            if 'error' in result and result['error']:
                return Response(
                    result,
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # WHAT: Serialize and return response
            # WHY: Ensure consistent response format
            # HOW: Use response serializer
            response_serializer = ExtractionResponseSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to process upload for trade {trade_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to process file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PreviewDropView(APIView):
    """
    WHAT: Preview which assets will be kept/dropped
    WHY: User needs to review before confirming
    HOW: Match IDs against database, return categorized results
    
    POST /api/acq/awarded-assets/preview/
    Body:
        {
            "trade_id": 123,
            "awarded_ids": ["ABC123", "DEF456", ...]
        }
    
    Response:
        {
            "matched_assets": [...],
            "will_be_dropped": [...],
            "unmatched_ids": [...],
            "summary": {...}
        }
    """
    parser_classes = [JSONParser]
    
    def get_permissions(self):
        """Bypass auth in DEBUG mode"""
        if settings.DEBUG:
            return []
        return [IsAuthenticated()]
    
    def post(self, request):
        """
        WHAT: Generate preview of drop operation
        WHY: Show user what will happen before executing
        HOW: Call service preview method
        """
        # WHAT: Validate request
        # WHY: Ensure we have required data
        serializer = ConfirmDropSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trade_id = serializer.validated_data['trade_id']
        awarded_ids = serializer.validated_data['awarded_ids']
        
        logger.info(f"Generating drop preview for trade {trade_id} with {len(awarded_ids)} awarded IDs")
        
        try:
            # WHAT: Generate preview
            # WHY: Show user impact of operation
            # HOW: Call service method
            service = AwardedAssetsService(trade_id=trade_id)
            preview = service.preview_drop(awarded_ids)
            
            # WHAT: Serialize response
            # WHY: Ensure consistent format
            response_serializer = PreviewResponseSerializer(data=preview)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to generate preview for trade {trade_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to generate preview: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmDropView(APIView):
    """
    WHAT: Execute the drop operation
    WHY: User confirmed they want to drop non-awarded assets
    HOW: Update acquisition_status to DROP for non-awarded
    
    POST /api/acq/awarded-assets/confirm/
    Body:
        {
            "trade_id": 123,
            "awarded_ids": ["ABC123", "DEF456", ...]
        }
    
    Response:
        {
            "success": true,
            "kept_count": 250,
            "dropped_count": 250,
            "message": "..."
        }
    """
    parser_classes = [JSONParser]
    
    def get_permissions(self):
        """Bypass auth in DEBUG mode"""
        if settings.DEBUG:
            return []
        return [IsAuthenticated()]
    
    def post(self, request):
        """
        WHAT: Execute drop operation
        WHY: User confirmed the action
        HOW: Call service execute method
        """
        # WHAT: Validate request
        # WHY: Ensure we have required data
        serializer = ConfirmDropSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trade_id = serializer.validated_data['trade_id']
        awarded_ids = serializer.validated_data['awarded_ids']
        
        # WHAT: Get user for audit trail
        # WHY: Track who performed the drop
        # HOW: Get from request or None
        user = request.user if request.user.is_authenticated else None
        
        logger.info(
            f"Executing drop for trade {trade_id} with {len(awarded_ids)} awarded IDs "
            f"(user: {user.username if user else 'anonymous'})"
        )
        
        try:
            # WHAT: Execute drop
            # WHY: User confirmed
            # HOW: Call service method
            service = AwardedAssetsService(trade_id=trade_id)
            result = service.execute_drop(awarded_ids, user=user)
            
            # WHAT: Serialize response
            # WHY: Ensure consistent format
            response_serializer = ExecuteResponseSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to execute drop for trade {trade_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to execute drop: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UndoDropView(APIView):
    """
    WHAT: Undo drop operation by restoring assets to KEEP status
    WHY: Allow users to fix mistakes
    HOW: Update acquisition_status back to KEEP
    
    POST /api/acq/awarded-assets/undo/
    Body:
        {
            "trade_id": 123,
            "asset_ids": [1, 2, 3]  // optional - if not provided, restores all
        }
    
    Response:
        {
            "success": true,
            "restored_count": 50,
            "message": "..."
        }
    """
    parser_classes = [JSONParser]
    
    def get_permissions(self):
        """Bypass auth in DEBUG mode"""
        if settings.DEBUG:
            return []
        return [IsAuthenticated()]
    
    def post(self, request):
        """
        WHAT: Restore dropped assets
        WHY: User wants to undo
        HOW: Call service undo method
        """
        # WHAT: Validate request
        # WHY: Ensure we have required data
        serializer = UndoDropSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        trade_id = serializer.validated_data['trade_id']
        asset_ids = serializer.validated_data.get('asset_ids')
        
        logger.info(
            f"Undoing drop for trade {trade_id} "
            f"({'specific assets' if asset_ids else 'all dropped assets'})"
        )
        
        try:
            # WHAT: Execute undo
            # WHY: Restore assets
            # HOW: Call service method
            service = AwardedAssetsService(trade_id=trade_id)
            result = service.undo_drop(asset_ids=asset_ids)
            
            # WHAT: Serialize response
            # WHY: Ensure consistent format
            response_serializer = UndoResponseSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to undo drop for trade {trade_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to undo drop: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DropHistoryView(APIView):
    """
    WHAT: Get history of dropped assets for a trade
    WHY: Show user current state
    HOW: Query dropped assets and return summary
    
    GET /api/acq/awarded-assets/history/{trade_id}/
    
    Response:
        {
            "dropped_assets": [...],
            "dropped_count": 50,
            "kept_count": 250,
            "trade_name": "..."
        }
    """
    def get_permissions(self):
        """Bypass auth in DEBUG mode"""
        if settings.DEBUG:
            return []
        return [IsAuthenticated()]
    
    def get(self, request, trade_id):
        """
        WHAT: Get drop history
        WHY: Show current state
        HOW: Call service method
        """
        logger.info(f"Fetching drop history for trade {trade_id}")
        
        try:
            # WHAT: Get history
            # WHY: Show user what's dropped
            # HOW: Call service method
            service = AwardedAssetsService(trade_id=trade_id)
            history = service.get_drop_history()
            
            # WHAT: Serialize response
            # WHY: Ensure consistent format
            response_serializer = DropHistorySerializer(data=history)
            response_serializer.is_valid(raise_exception=True)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch history for trade {trade_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to fetch history: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
