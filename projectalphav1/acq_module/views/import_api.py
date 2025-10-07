"""
API endpoint for importing seller data tapes via file upload.

WHAT: Handles file upload and triggers the ETL management command
WHY: Allows users to import Excel/CSV files from the frontend UI
HOW: Receives file, saves temporarily, executes Django management command, returns results

Documentation reviewed:
- Django file uploads: https://docs.djangoproject.com/en/5.2/topics/http/file-uploads/
- DRF APIView: https://www.django-rest-framework.org/api-guide/views/
- Django management commands: https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/
"""
import os
import tempfile
import subprocess
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
def import_seller_tape(request):
    """
    WHAT: API endpoint to upload and import seller data tape files
    WHY: Provides UI-driven import functionality using the ETL command
    HOW: Saves uploaded file temporarily, calls management command, returns results
    
    Request body:
    - file: Excel/CSV file (multipart/form-data)
    - seller_name: str (required)
    - trade_name: str (optional)
    - auto_create: bool (default: true)
    - dry_run: bool (default: false)
    
    Returns:
    - 200: Success with import results
    - 400: Validation error
    - 500: Import failed
    """
    try:
        # Validate file upload
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file: UploadedFile = request.FILES['file']
        seller_name = request.data.get('seller_name', '').strip()
        trade_name = request.data.get('trade_name', '').strip()
        auto_create = request.data.get('auto_create', 'true').lower() == 'true'
        dry_run = request.data.get('dry_run', 'false').lower() == 'true'
        
        # Validate seller name
        if not seller_name:
            return Response(
                {'error': 'Seller name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file extension
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.xlsx', '.xls', '.csv']:
            return Response(
                {'error': f'Invalid file type: {file_ext}. Only Excel (.xlsx, .xls) and CSV (.csv) files are supported.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file to temporary location
        # WHAT: Create temporary file to store upload
        # WHY: Management command needs a file path to read from
        # HOW: Use tempfile to create secure temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Write uploaded file to temp location
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Build management command arguments
            # WHAT: Construct command to call import_seller_data management command
            # WHY: Reuse existing ETL logic instead of duplicating code
            # HOW: Use subprocess to call Django management command
            cmd = [
                'python',
                'manage.py',
                'import_seller_data',
                '--file', temp_file_path,
                '--seller-name', seller_name,
            ]
            
            if trade_name:
                cmd.extend(['--trade-name', trade_name])
            
            if auto_create:
                cmd.append('--auto-create')
            
            if dry_run:
                cmd.append('--dry-run')
            
            # Execute management command
            # WHAT: Run the import command and capture output
            # WHY: Need to return results to frontend
            # HOW: subprocess.run with capture_output=True
            logger.info(f'Executing import command: {" ".join(cmd)}')
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # Project root
                timeout=300  # 5 minute timeout
            )
            
            # Check if command succeeded
            if result.returncode == 0:
                # Success
                return Response({
                    'success': True,
                    'message': 'Import completed successfully!',
                    'output': result.stdout,
                    'dry_run': dry_run
                })
            else:
                # Command failed
                logger.error(f'Import command failed: {result.stderr}')
                return Response({
                    'error': 'Import failed',
                    'details': result.stderr or result.stdout,
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Clean up temporary file
            # WHAT: Delete temporary file after processing
            # WHY: Prevent disk space issues from accumulating temp files
            # HOW: os.unlink to remove file
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f'Failed to delete temp file {temp_file_path}: {e}')
    
    except subprocess.TimeoutExpired:
        return Response({
            'error': 'Import timeout',
            'details': 'Import took longer than 5 minutes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.exception('Unexpected error during import')
        return Response({
            'error': 'Import failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
